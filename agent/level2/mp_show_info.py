#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子进程状态信息聚合器

通过共享内存收集所有子进程的状态，供外部监控/调试使用。

支持进程:
  - RealSense 相机进程
  - 麦克风录音识别进程
  - TTS 语音播报进程
  - Robot State 进程

用法:
    # 获取所有进程状态
    status = get_all_status()
    print(status)

    # 启动状态监控 (定期打印)
    monitor_status(callback=print)
"""

import time
import struct
import threading
from typing import Optional, Callable
from multiprocessing import shared_memory
import numpy as np

# ======================================================================
# 共享内存状态管理
# ======================================================================
class ProcessStatus:
    """
    单个进程的状态信息结构

    共享内存布局 (共 280 bytes):
    - [0:8]   is_ready: uint8 (0/1)
    - [8:16]  is_running: uint8 (0/1)
    - [16:24] error_flag: uint8 (0/1)
    - [24:32] last_update: float64 (时间戳)
    - [32:288] message: bytes (256 bytes, UTF-8 状态消息)
    """

    SIZE = 288  # 总大小

    def __init__(self, shm: shared_memory.SharedMemory):
        self._shm = shm
        self._buf = shm.buf

    @classmethod
    def create(cls, name: str):
        """创建新的状态共享内存"""
        shm = shared_memory.SharedMemory(name=name, create=True, size=cls.SIZE)
        # 初始化为 0
        for i in range(cls.SIZE):
            shm.buf[i] = 0
        return cls(shm)

    @classmethod
    def connect(cls, name: str):
        """连接到已有状态共享内存"""
        shm = shared_memory.SharedMemory(name=name, create=False)
        return cls(shm)

    @property
    def name(self) -> str:
        return self._shm.name

    @property
    def is_ready(self) -> int:
        return self._buf[0]

    @is_ready.setter
    def is_ready(self, val: int):
        self._buf[0] = 1 if val else 0
        self._touch()

    @property
    def is_running(self) -> int:
        return self._buf[8]

    @is_running.setter
    def is_running(self, val: int):
        self._buf[8] = 1 if val else 0
        self._touch()

    @property
    def error_flag(self) -> int:
        return self._buf[16]

    @error_flag.setter
    def error_flag(self, val: int):
        self._buf[16] = 1 if val else 0
        self._touch()

    @property
    def last_update(self) -> float:
        return struct.unpack_from('d', self._buf, 24)[0]

    @property
    def message(self) -> str:
        msg_bytes = bytes(self._buf[32:288])
        # 找到 null 终止符
        null_pos = msg_bytes.find(b'\x00')
        if null_pos >= 0:
            msg_bytes = msg_bytes[:null_pos]
        try:
            return msg_bytes.decode('utf-8').strip()
        except Exception:
            return msg_bytes.decode('utf-8', errors='ignore').strip()

    def set_message(self, msg: str):
        """设置状态消息 (最多 256 字节)"""
        msg_bytes = msg.encode('utf-8')[:256]
        msg_bytes = msg_bytes + b'\x00' * (256 - len(msg_bytes))
        self._buf[32:288] = msg_bytes
        self._touch()

    def _touch(self):
        """更新最后更新时间"""
        struct.pack_into('d', self._buf, 24, time.time())

    def get_dict(self) -> dict:
        """获取状态字典"""
        return {
            'name': self._shm.name,
            'is_ready': bool(self.is_ready),
            'is_running': bool(self.is_running),
            'error_flag': bool(self.error_flag),
            'last_update': self.last_update,
            'message': self.message,
        }

    def set_error(self, error_msg: str):
        """设置错误状态"""
        self.error_flag = 1
        self.set_message(error_msg)

    def clear_error(self):
        """清除错误状态"""
        self.error_flag = 0

    def close(self):
        self._shm.close()

    def unlink(self):
        try:
            self._shm.unlink()
        except FileNotFoundError:
            pass


# ======================================================================
# 状态注册表
# ======================================================================
class StatusRegistry:
    """
    管理所有进程状态的注册表

    主进程使用，用于创建/连接各子进程的状态共享内存
    """

    # 预定义进程名称
    PROCESS_REALSENSE = "realsense"
    PROCESS_AUDIO = "audio"
    PROCESS_TTS = "tts"
    PROCESS_ROBOT_STATE = "robot_state"

    _STATUS_NAMES = {
        PROCESS_REALSENSE: "RealSense 相机",
        PROCESS_AUDIO: "麦克风录音",
        PROCESS_TTS: "TTS 播报",
        PROCESS_ROBOT_STATE: "机器人状态",
    }

    def __init__(self):
        self._statuses: dict[str, ProcessStatus] = {}
        self._lock = threading.Lock()

    def create_status(self, process_name: str) -> ProcessStatus:
        """
        创建指定进程的状态共享内存

        Args:
            process_name: 进程标识名 (如 "realsense", "audio", "tts")

        Returns:
            ProcessStatus 实例
        """
        shm_name = f"status_{process_name}"

        with self._lock:
            if process_name in self._statuses:
                return self._statuses[process_name]

            status = ProcessStatus.create(name=shm_name)
            self._statuses[process_name] = status
            return status

    def connect_status(self, process_name: str) -> ProcessStatus:
        """
        连接到已存在的状态共享内存

        Args:
            process_name: 进程标识名

        Returns:
            ProcessStatus 实例
        """
        shm_name = f"status_{process_name}"

        with self._lock:
            if process_name in self._statuses:
                return self._statuses[process_name]

            status = ProcessStatus.connect(name=shm_name)
            self._statuses[process_name] = status
            return status

    def get_all_status(self) -> dict:
        """获取所有已注册进程的状态"""
        result = {}
        with self._lock:
            for name, status in self._statuses.items():
                result[name] = status.get_dict()
        return result

    def close_all(self):
        """关闭所有状态连接"""
        with self._lock:
            for status in self._statuses.values():
                status.close()
            self._statuses.clear()

    @staticmethod
    def get_process_display_name(process_name: str) -> str:
        """获取进程的中文显示名称"""
        return StatusRegistry._STATUS_NAMES.get(process_name, process_name)


# ======================================================================
# 全局单例
# ======================================================================
_global_registry: Optional[StatusRegistry] = None


def get_status_registry() -> StatusRegistry:
    """获取全局状态注册表"""
    global _global_registry
    if _global_registry is None:
        _global_registry = StatusRegistry()
    return _global_registry


# ======================================================================
# 便捷 API
# ======================================================================
def get_all_status() -> dict:
    """获取所有子进程状态 (快捷函数)"""
    return get_status_registry().get_all_status()


def print_all_status() -> str:
    """打印所有状态，返回格式化字符串"""
    statuses = get_all_status()

    lines = []
    lines.append("=" * 60)
    lines.append("子进程状态监控")
    lines.append("=" * 60)

    for name, info in statuses.items():
        display_name = StatusRegistry.get_process_display_name(name)
        lines.append(f"\n[{name}] {display_name}")

        ready_str = "✓ 已就绪" if info['is_ready'] else "○ 未就绪"
        running_str = "● 运行中" if info['is_running'] else "○ 已停止"
        error_str = " ⚠ 错误" if info['error_flag'] else ""

        lines.append(f"  状态: {ready_str} | {running_str}{error_str}")

        if info['message']:
            lines.append(f"  消息: {info['message']}")

        if info['last_update'] > 0:
            age = time.time() - info['last_update']
            lines.append(f"  更新: {age:.1f}s 前")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def monitor_status(
    interval: float = 2.0,
    callback: Optional[Callable[[str], None]] = None,
    stop_event=None
):
    """
    定期监控并打印状态

    Args:
        interval: 打印间隔 (秒)
        callback: 自定义回调函数 (接收格式化字符串)
        stop_event: 停止事件 (threading.Event)
    """
    print("[StatusMonitor] 开始状态监控 (Ctrl+C 退出)")

    try:
        while True:
            if stop_event and stop_event.is_set():
                break

            output = print_all_status()
            if callback:
                callback(output)
            else:
                print(output)

            # 检查是否所有进程都已就绪
            statuses = get_all_status()
            all_ready = all(s['is_ready'] for s in statuses.values())
            if all_ready:
                print("[StatusMonitor] 所有进程已就绪，监控继续中...")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[StatusMonitor] 监控已停止")


# ======================================================================
# 测试
# ======================================================================
if __name__ == "__main__":
    print("--- 状态监控系统测试 ---\n")

    registry = get_status_registry()

    # 模拟创建多个进程状态
    print("创建测试状态...")
    realsense_status = registry.create_status(StatusRegistry.PROCESS_REALSENSE)
    audio_status = registry.create_status(StatusRegistry.PROCESS_AUDIO)
    tts_status = registry.create_status(StatusRegistry.PROCESS_TTS)

    # 更新状态
    realsense_status.is_ready = True
    realsense_status.is_running = True
    realsense_status.set_message("相机正常工作中")

    audio_status.is_ready = True
    audio_status.is_running = True
    audio_status.set_message("等待唤醒词...")

    tts_status.is_ready = True
    tts_status.is_running = True
    tts_status.set_message("TTS 就绪")

    # 模拟错误状态
    error_status = registry.create_status("error_test")
    error_status.is_ready = True
    error_status.is_running = True
    error_status.set_error("模拟错误: 连接失败")

    # 打印所有状态
    print(print_all_status())

    # 清理
    print("\n清理测试状态...")
    registry.close_all()

    # 清理共享内存
    for name in ["realsense", "audio", "tts", "error_test"]:
        try:
            shm = shared_memory.SharedMemory(name=f"status_{name}", create=False)
            shm.close()
            shm.unlink()
        except FileNotFoundError:
            pass

    print("测试完成!")
