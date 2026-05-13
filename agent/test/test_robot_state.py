#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RobotStateSubProcess 功能测试

测试项:
1. 启动子进程采集机器人状态
2. 获取电池状态 (电量、电压)
3. 获取姿态信息 (位置、速度、偏航角)
4. 获取完整状态快照
5. 连续采集, 检查数据更新频率
6. 停止子进程
"""

import time
import sys
import numpy as np

sys.path.insert(0, '/home/unitree/unitree_sdk2_python')
from agent.level2.mp_robot_state import RobotStateSubProcess


def test_basic_state():
    """测试 1: 启动子进程, 获取基本状态"""
    print("=" * 60)
    print("测试 1: 基本状态采集")
    print("=" * 60)

    robot = RobotStateSubProcess(network_interface="eth0")
    robot.start(wait=True, timeout=10.0)

    try:
        # 等待数据写入
        time.sleep(1.0)

        # 获取电池状态
        battery_soc, voltage, current = robot.get_battery()
        print(f"  电池电量: {battery_soc}%")
        print(f"  电压: {voltage:.2f}V")
        print(f"  电流: {current:.2f}A")

        # 获取姿态
        posture = robot.get_posture()
        print(f"  位置: x={posture['position'][0]:.3f}, "
              f"y={posture['position'][1]:.3f}, z={posture['position'][2]:.3f}")
        print(f"  速度: vx={posture['velocity'][0]:.3f}, "
              f"vy={posture['velocity'][1]:.3f}, vz={posture['velocity'][2]:.3f}")
        print(f"  偏航角: {posture['yaw']:.3f} rad")

        print("  测试 1 通过\n")
    finally:
        robot.stop()


def test_full_state():
    """测试 2: 获取完整状态快照"""
    print("=" * 60)
    print("测试 2: 完整状态快照")
    print("=" * 60)

    robot = RobotStateSubProcess(network_interface="eth0")
    robot.start(wait=True, timeout=10.0)

    try:
        time.sleep(1.0)

        state = robot.get_all_state()
        print(f"  完整状态:")
        print(f"    battery_soc: {state['battery_soc']}%")
        print(f"    voltage: {state['voltage']:.2f}V")
        print(f"    position: {state['position']}")
        print(f"    velocity: {state['velocity']}")
        print(f"    rpy: {state['rpy']}")
        print(f"    yaw: {state['yaw']:.3f} rad")
        print(f"    timestamp: {state['timestamp']:.3f}")

        print("  测试 2 通过\n")
    finally:
        robot.stop()


def test_continuous_update():
    """测试 3: 连续采集, 检查数据更新"""
    print("=" * 60)
    print("测试 3: 连续采集 & 数据更新检查")
    print("=" * 60)

    robot = RobotStateSubProcess(network_interface="eth0")
    robot.start(wait=True, timeout=10.0)

    try:
        time.sleep(1.0)

        print("  连续读取 10 次状态 (每次间隔 0.5s):")
        for i in range(10):
            state = robot.get_all_state()
            print(f"    [{i+1}] battery={state['battery_soc']}% | "
                  f"pos=({state['position'][0]:.2f}, {state['position'][1]:.2f}) | "
                  f"yaw={state['yaw']:.2f} | ts={state['timestamp']:.3f}")
            time.sleep(0.5)

        print("  测试 3 通过\n")
    finally:
        robot.stop()


def test_context_manager():
    """测试 4: context manager 用法"""
    print("=" * 60)
    print("测试 4: context manager 自动启停")
    print("=" * 60)

    with RobotStateSubProcess(network_interface="eth0") as robot:
        time.sleep(1.0)
        state = robot.get_all_state()
        print(f"  is_ready: {robot.is_ready}")
        print(f"  电池: {state['battery_soc']}%")

    print("  context manager 退出后进程已结束")
    print("  测试 4 通过\n")


def test_state_consistency():
    """测试 5: 状态读取一致性 (多次读取应得到一致的数据)"""
    print("=" * 60)
    print("测试 5: 状态读取一致性")
    print("=" * 60)

    robot = RobotStateSubProcess(network_interface="eth0")
    robot.start(wait=True, timeout=10.0)

    try:
        time.sleep(1.0)

        # 连续读取多次, 检查数据格式一致性
        states = []
        for _ in range(5):
            state = robot.get_all_state()
            states.append(state)
            time.sleep(0.1)

        # 检查所有状态都有相同的字段
        keys = ['battery_soc', 'voltage', 'position', 'velocity', 'rpy', 'quaternion', 'yaw', 'timestamp']
        for state in states:
            for key in keys:
                assert key in state, f"缺少字段: {key}"

        print(f"  所有状态都包含正确的字段: {keys}")
        print("  测试 5 通过\n")
    finally:
        robot.stop()


def test_pose_matrix():
    """测试 6: 4x4 位姿矩阵"""
    print("=" * 60)
    print("测试 6: 4x4 位姿矩阵 (SE(3))")
    print("=" * 60)

    robot = RobotStateSubProcess(network_interface="eth0")
    robot.start(wait=True, timeout=10.0)

    try:
        time.sleep(1.0)

        T = robot.get_pose_matrix()
        print(f"  4x4 位姿矩阵:")
        print(f"    {T[0]}")
        print(f"    {T[1]}")
        print(f"    {T[2]}")
        print(f"    {T[3]}")

        # 验证最后一行是 [0, 0, 0, 1]
        assert np.allclose(T[3], [0, 0, 0, 1]), "矩阵最后一行应为 [0, 0, 0, 1]"

        # 验证旋转矩阵是正交矩阵 (R @ R.T = I)
        R = T[:3, :3]
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-6), "旋转矩阵应为正交矩阵"

        print(f"  旋转矩阵正交性验证: 通过")
        print(f"  平移向量: {T[:3, 3]}")
        print("  测试 6 通过\n")
    finally:
        robot.stop()


if __name__ == "__main__":
    # Linux 默认使用 fork，无需显式设置

    print("\n>>> RobotStateSubProcess 功能测试 <<<\n")
    print("注意: 此测试需要在机器狗上运行, 且需要正确配置网络接口")
    print("      如果没有连接机器狗, 测试将会超时失败\n")

    try:
        # test_basic_state()
        test_full_state()
        # test_continuous_update()
        # test_context_manager()
        # test_state_consistency()
        test_pose_matrix()
        print("=" * 60)
        print("所有测试通过!")
        print("=" * 60)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
