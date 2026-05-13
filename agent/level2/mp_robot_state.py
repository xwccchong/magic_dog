#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器狗状态多进程采集模块

架构:
- 子进程: 运行 DDS 订阅回调, 持续将状态写入共享内存
- 主进程: 零拷贝读取最新状态

与 robot_state.py (多线程版) 的区别:
  - DDS 回调完全隔离在子进程, 不占用主进程资源
  - 使用共享内存而非线程锁, 适合与 CPU 密集任务并行
  - Linux 系统使用 fork 模式，性能更优

用法:
    from level2.robot_state_mp import RobotStateSubProcess

    robot = RobotStateSubProcess(network_interface="eth0")
    robot.start()

    state = robot.get_all_state()
    battery, voltage, current = robot.get_battery()
    posture = robot.get_posture()

    robot.stop()
"""

import sys
import time
import multiprocessing as mp
import numpy as np
from typing import Optional

from .shared_memory_buffer import SharedMemoryArray


# ======================================================================
# 子进程入口: DDS 订阅 + 写入共享内存
# ======================================================================
def _robot_state_worker(
    shm_name: str,
    shm_unit_shape: int,
    network_interface: str,
    stop_event: mp.Event,
    ready_event: mp.Event,
):
    """子进程: 初始化 DDS 订阅, 在回调中将状态写入共享内存"""
    import cv2
    cv2.setNumThreads(1)

    # 连接到共享数组
    state_arr = SharedMemoryArray.connect(
        name=shm_name,
        shape=(shm_unit_shape,),
        dtype=np.float64,
    )

    # ---- 初始化 DDS ----
    # 子进程需要确保 LD_LIBRARY_PATH 包含 cyclonedds 库路径
    import os
    cyclonedds_lib = os.path.expanduser('~/cyclonedds_ws/install/cyclonedds/lib')
    current_ld = os.environ.get('LD_LIBRARY_PATH', '')
    if cyclonedds_lib not in current_ld:
        os.environ['LD_LIBRARY_PATH'] = cyclonedds_lib + ':' + current_ld

    sys.path.insert(0, '/home/unitree/unitree_sdk2_python')
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_

    ChannelFactoryInitialize(0, network_interface)

    seq_counter = 0

    def _write_state(battery_soc=None, voltage=None, current=None,
                     position=None, velocity=None, rpy=None, quaternion=None):
        """写入状态到共享数组"""
        nonlocal seq_counter

        # 读取当前数据, 部分更新
        data, seq = state_arr.read_no_copy()
        # data, _ = state_arr.read_no_copy()

        if battery_soc is not None:
            data[0] = float(battery_soc)
        if voltage is not None:
            data[1] = float(voltage)
        if current is not None:
            data[2] = float(current)
        if position is not None:
            data[3] = position[0]
            data[4] = position[1]
            data[5] = position[2]
        if velocity is not None:
            data[6] = velocity[0]
            data[7] = velocity[1]
            data[8] = velocity[2]
        if rpy is not None:
            data[9] = rpy[0]   # roll
            data[10] = rpy[1]  # pitch
            data[11] = rpy[2]  # yaw
        if quaternion is not None:
            data[12] = quaternion[0]  # w
            data[13] = quaternion[1]  # x
            data[14] = quaternion[2]  # y
            data[15] = quaternion[3]  # z

        data[16] = time.monotonic()
        seq_counter += 1
        state_arr.write(data, seq=seq_counter)

    def _low_state_handler(msg: LowState_):
        _write_state(
            battery_soc=msg.bms_state.soc,
            voltage=msg.power_v,
            current=msg.power_a,
        )

    def _sport_state_handler(msg: SportModeState_):
        _write_state(
            position=[msg.position[0], msg.position[1], msg.position[2]],
            velocity=[msg.velocity[0], msg.velocity[1], msg.velocity[2]],
            rpy=[msg.imu_state.rpy[0], msg.imu_state.rpy[1], msg.imu_state.rpy[2]],
            quaternion=[msg.imu_state.quaternion[0], msg.imu_state.quaternion[1],
                       msg.imu_state.quaternion[2], msg.imu_state.quaternion[3]],
        )

    sub_low = ChannelSubscriber("rt/lowstate", LowState_)
    sub_low.Init(_low_state_handler, 10)

    sub_sport = ChannelSubscriber("rt/sportmodestate", SportModeState_)
    sub_sport.Init(_sport_state_handler, 10)

    ready_event.set()
    print(f"[RobotState-SubProcess] DDS 订阅已就绪 (接口: {network_interface})")

    # 保持子进程存活, 直到 stop
    while not stop_event.is_set():
        time.sleep(0.1)

    state_arr.close()


# ======================================================================
# 主进程端 API
# ======================================================================
class RobotStateSubProcess:
    """
    机器狗状态多进程封装

    - 子进程运行 DDS 订阅, 将状态写入共享内存
    - 主进程零拷贝读取最新状态
    - 支持 context manager
    """

    # 共享数组布局:
    # [0-2]: battery_soc, voltage, current
    # [3-5]: position (x, y, z)
    # [6-8]: velocity (vx, vy, vz)
    # [9-11]: rpy (roll, pitch, yaw)
    # [12-15]: quaternion (w, x, y, z)
    # [16]: timestamp
    STATE_SHAPE = (17,)

    def __init__(self, network_interface: str = "eth0"):
        self._network_interface = network_interface

        # 创建共享数组
        self._state_arr = SharedMemoryArray.create(
            shape=self.STATE_SHAPE,
            dtype=np.float64,
        )

        self._stop_event = mp.Event()
        self._ready_event = mp.Event()
        self._process: Optional[mp.Process] = None

    # ---- context manager ----
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    # ---- 生命周期 ----
    def start(self, wait=True, timeout=10.0):
        """启动状态采集子进程"""
        if self._process is not None and self._process.is_alive():
            print("[RobotState-SubProcess] 采集进程已在运行")
            return

        self._stop_event.clear()
        self._ready_event.clear()

        self._process = mp.Process(
            target=_robot_state_worker,
            args=(
                self._state_arr.name,
                self.STATE_SHAPE[0],
                self._network_interface,
                self._stop_event,
                self._ready_event,
            ),
            daemon=True,
        )
        self._process.start()

        if wait:
            if not self._ready_event.wait(timeout=timeout):
                raise TimeoutError(
                    f"[RobotState-SubProcess] 子进程未在 {timeout}s 内就绪"
                )

    def stop(self, wait=True):
        """停止采集子进程并释放共享内存"""
        self._stop_event.set()

        if self._process is not None:
            if wait:
                self._process.join(timeout=3.0)
                if self._process.is_alive():
                    self._process.kill()
                    self._process.join(timeout=2.0)
            self._process = None

        self._state_arr.close()
        self._state_arr.unlink()
        print("[RobotState-SubProcess] 已停止, 资源已释放")

    @property
    def is_ready(self) -> bool:
        return self._ready_event.is_set()

    # ---- 内部: 读取状态 ----
    def _read_state(self) -> dict:
        """读取共享内存中的最新状态"""
        data, _ = self._state_arr.read()

        return {
            "battery_soc": int(data[0]),
            "voltage": float(data[1]),
            "current": float(data[2]),
            "position": [float(data[3]), float(data[4]), float(data[5])],
            "velocity": [float(data[6]), float(data[7]), float(data[8])],
            "rpy": [float(data[9]), float(data[10]), float(data[11])],  # roll, pitch, yaw
            "quaternion": [float(data[12]), float(data[13]), float(data[14]), float(data[15])],  # w, x, y, z
            "yaw": float(data[11]),  # 保持向后兼容
            "timestamp": float(data[16]),
        }

    # ---- 对外接口 (与原 robot_state.py 保持一致) ----
    def get_battery(self):
        """获取当前电量, 电压, 电流 -> (soc, voltage, current)"""
        state = self._read_state()
        return state["battery_soc"], state["voltage"], state["current"]

    def get_posture(self):
        """获取当前位置、速度与偏航角 -> dict"""
        state = self._read_state()
        return {
            "position": state["position"],
            "velocity": state["velocity"],
            "yaw": state["yaw"],
        }

    def get_all_state(self):
        """获取完整状态快照 -> dict"""
        return self._read_state()

    def get_pose_matrix(self) -> np.ndarray:
        """
        获取 4x4 位姿变换矩阵 (SE(3))

        返回:
            np.ndarray: 4x4 齐次变换矩阵
            | R R R tx |
            | R R R ty |
            | R R R tz |
            | 0 0 0 1  |
        """
        state = self._read_state()
        position = np.array(state["position"])
        quaternion = state["quaternion"]  # [w, x, y, z]

        # 四元数转旋转矩阵
        w, x, y, z = quaternion

        # 旋转矩阵元素
        r00 = 1 - 2*(y*y + z*z)
        r01 = 2*(x*y - z*w)
        r02 = 2*(x*z + y*w)

        r10 = 2*(x*y + z*w)
        r11 = 1 - 2*(x*x + z*z)
        r12 = 2*(y*z - x*w)

        r20 = 2*(x*z - y*w)
        r21 = 2*(y*z + x*w)
        r22 = 1 - 2*(x*x + y*y)

        # 构建 4x4 矩阵
        T = np.eye(4)
        T[0, :3] = [r00, r01, r02]
        T[1, :3] = [r10, r11, r12]
        T[2, :3] = [r20, r21, r22]
        T[:3, 3] = position

        return T


# ======================================================================
# 便捷入口
# ======================================================================
if __name__ == "__main__":
    # Linux 默认使用 fork，无需显式设置

    print("--- RobotState 多进程测试 ---")
    robot = RobotStateSubProcess(network_interface="eth0")
    robot.start()

    try:
        for i in range(10):
            time.sleep(1.0)
            state = robot.get_all_state()
            print(
                f"[{i+1}] "
                f"battery={state['battery_soc']}% voltage={state['voltage']} current={state['voltage']:.1f}V | "
                f"pos=({state['position'][0]:.2f}, {state['position'][1]:.2f}, {state['position'][2]:.2f}) | "
                f"velocity=({state['velocity'][0]:.2f}, {state['velocity'][1]:.2f}, {state['velocity'][2]:.2f}) "
                f"yaw={state['yaw']:.3f}"
            )
    finally:
        robot.stop()
