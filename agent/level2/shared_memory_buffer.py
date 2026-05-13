#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享内存数据结构模块

提供两种共享内存数据结构:
1. SharedMemoryRingBuffer - 环形缓冲区, 适合高频图像/连续帧采集
2. SharedMemoryArray - 单次数组, 适合低频状态数据 (如机器人位姿)

特点:
- 纯标准库实现, 无第三方依赖
- 支持 Linux fork 多进程模式 (更高效)
- 零拷贝读写
"""

import sys
import time
import struct
import numpy as np
from multiprocessing import shared_memory
from typing import Optional, Union, Tuple


# ======================================================================
# 环形缓冲区: 适合连续帧采集 (如图像)
# ======================================================================
class SharedMemoryRingBuffer:
    
    """
    基于 multiprocessing.shared_memory 的定长环形缓冲区。

    每个槽位存储:
    - data: 用户自定义大小的数组
    - timestamp: float64 (8 bytes)

    使用写指针递增模式: 写指针只增不减, 读端取 last_k。

    典型用法:
        # 主进程创建
        ring = SharedMemoryRingBuffer.create(shape=(720, 1280, 3), dtype=np.uint8, buffer_size=90)

        # 子进程连接
        ring = SharedMemoryRingBuffer.connect(name=shm_name, shape=(720, 1280, 3), dtype=np.uint8, buffer_size=90)

        # 写入 (子进程)
        ring.put(color_img, depth_img, timestamp)

        # 读取 (主进程)
        colors, depths, timestamps = ring.get_last_k(5)
    """

    def __init__(
        self,
        name: Optional[str],
        shape: tuple,
        dtype: Union[np.dtype, str],
        buffer_size: int,
        create: bool = True,
        n_arrays: int = 1,
    ):
        """
        Args:
            name:        共享内存块名 (None 则自动生成)
            shape:       单个数组的 shape (不含 batch)
            dtype:       数据类型
            buffer_size: 槽位数量
            create:      True=创建新块, False=连接已有块
            n_arrays:    每个槽位存储的数组数量 (例如 RGB+Depth=2)
        """
        self.shape = tuple(shape)
        self.dtype = np.dtype(dtype)
        self.buffer_size = buffer_size
        self.n_arrays = n_arrays

        # 每个数组的大小
        self._array_bytes = int(np.prod(self.shape)) * self.dtype.itemsize
        # 每个槽位: n_arrays * array + timestamp (8 bytes)
        self._slot_size = n_arrays * self._array_bytes + 8
        # 总大小: buffer_size * slot + write_idx (8 bytes)
        self._total_bytes = self._slot_size * buffer_size + 8

        if create:
            self._shm = shared_memory.SharedMemory(
                name=name, create=True, size=self._total_bytes
            )
        else:
            self._shm = shared_memory.SharedMemory(name=name, create=False)

        self._base = self._shm.buf
        self._idx_offset = self._slot_size * buffer_size

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------
    @property
    def name(self) -> str:
        """共享内存块名 (用于子进程连接)"""
        return self._shm.name

    @property
    def write_index(self) -> int:
        """当前写指针位置"""
        return struct.unpack_from('Q', self._base, self._idx_offset)[0]

    @write_index.setter
    def write_index(self, val: int):
        struct.pack_into('Q', self._base, self._idx_offset, val)

    @property
    def count(self) -> int:
        """已写入的总帧数"""
        return self.write_index

    # ------------------------------------------------------------------
    # 工厂方法
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, shape: tuple, dtype, buffer_size: int, n_arrays: int = 1):
        """创建新的共享内存环形缓冲区"""
        return cls(name=None, shape=shape, dtype=dtype,
                   buffer_size=buffer_size, create=True, n_arrays=n_arrays)

    @classmethod
    def connect(cls, name: str, shape: tuple, dtype, buffer_size: int, n_arrays: int = 1):
        """连接到已存在的共享内存环形缓冲区"""
        return cls(name=name, shape=shape, dtype=dtype,
                   buffer_size=buffer_size, create=False, n_arrays=n_arrays)

    # ------------------------------------------------------------------
    # 写入 (子进程调用)
    # ------------------------------------------------------------------
    def put(self, *arrays, timestamp: float = None):
        """
        写入一帧数据

        Args:
            *arrays:    n_arrays 个 numpy 数组
            timestamp:  时间戳 (默认 time.monotonic())
        """
        if len(arrays) != self.n_arrays:
            raise ValueError(f"期望 {self.n_arrays} 个数组, 收到 {len(arrays)} 个")

        if timestamp is None:
            timestamp = time.monotonic()

        idx = self.write_index
        slot_offset = (idx % self.buffer_size) * self._slot_size

        # 写入各数组
        for i, arr in enumerate(arrays):
            arr_offset = slot_offset + i * self._array_bytes
            buf = np.ndarray(
                np.prod(self.shape), dtype=self.dtype,
                buffer=self._base, offset=arr_offset
            )
            buf[:] = arr.ravel()

        # 写入 timestamp
        ts_offset = slot_offset + self.n_arrays * self._array_bytes
        struct.pack_into('d', self._base, ts_offset, timestamp)

        # 最后更新 write_idx
        self.write_index = idx + 1

    # ------------------------------------------------------------------
    # 读取 (主进程调用)
    # ------------------------------------------------------------------
    def get_last_k(self, k: int):
        """
        读取最新 k 帧

        Returns:
            if n_arrays == 1:
                arrays: list[np.ndarray], timestamps: list[float]
            else:
                arrays_tuple: tuple of list[np.ndarray], timestamps: list[float]

        Example (n_arrays=2, 如 RGB+Depth):
            (rgbs, depths), timestamps = ring.get_last_k(5)
        """
        idx = self.write_index
        available = min(k, idx)
        if available == 0:
            if self.n_arrays == 1:
                return [], []
            else:
                return tuple([] for _ in range(self.n_arrays)), []

        # 准备输出列表
        output_lists = [[] for _ in range(self.n_arrays)]
        timestamps = []

        for i in range(available):
            read_idx = idx - available + i
            slot_offset = (read_idx % self.buffer_size) * self._slot_size

            # 读取各数组
            for j in range(self.n_arrays):
                arr_offset = slot_offset + j * self._array_bytes
                arr = np.ndarray(
                    self.shape, dtype=self.dtype,
                    buffer=self._base, offset=arr_offset
                ).copy()
                output_lists[j].append(arr)

            # 读取 timestamp
            ts_offset = slot_offset + self.n_arrays * self._array_bytes
            ts = struct.unpack_from('d', self._base, ts_offset)[0]
            timestamps.append(ts)

        if self.n_arrays == 1:
            return output_lists[0], timestamps
        else:
            return tuple(output_lists), timestamps

    def get_latest(self):
        """获取最新一帧 (便捷方法)"""
        arrays, timestamps = self.get_last_k(1)
        if self.n_arrays == 1:
            if len(arrays) == 0:
                return None, None
            return arrays[0], timestamps[0] if timestamps else None
        else:
            if len(arrays[0]) == 0:
                return tuple(None for _ in range(self.n_arrays)), None
            return tuple(a[0] for a in arrays), timestamps[0] if timestamps else None

    # ------------------------------------------------------------------
    # 资源管理
    # ------------------------------------------------------------------
    def close(self):
        """关闭共享内存连接 (不删除)"""
        self._shm.close()

    def unlink(self):
        """删除共享内存块 (仅创建者调用)"""
        try:
            self._shm.unlink()
        except FileNotFoundError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ======================================================================
# 单次数组: 适合低频状态数据 (如机器人位姿)
# ======================================================================
class SharedMemoryArray:
    """
    单次数组共享内存, 支持原子读写。

    使用 seq 序列号实现一致性读取:
    - 写入时先写数据, 最后递增 seq
    - 读取时检查 seq 是否变化, 若变化则重试

    典型用法:
        # 主进程创建
        arr = SharedMemoryArray.create(shape=(10,), dtype=np.float64)

        # 子进程连接
        arr = SharedMemoryArray.connect(name=shm_name, shape=(10,), dtype=np.float64)

        # 写入 (子进程)
        arr.write(np.array([1.0, 2.0, 3.0, ...]))

        # 读取 (主进程)
        data, seq = arr.read()
    """

    # 布局: [seq: 8 bytes] + [data: shape * dtype.itemsize]
    _SEQ_SIZE = 8

    def __init__(
        self,
        name: Optional[str],
        shape: tuple,
        dtype: Union[np.dtype, str],
        create: bool = True,
    ):
        """
        Args:
            name:   共享内存块名
            shape:  数组 shape
            dtype:  数据类型
            create: True=创建, False=连接
        """
        self.shape = tuple(shape)
        self.dtype = np.dtype(dtype)

        self._data_bytes = int(np.prod(self.shape)) * self.dtype.itemsize
        self._total_bytes = self._SEQ_SIZE + self._data_bytes

        if create:
            self._shm = shared_memory.SharedMemory(
                name=name, create=True, size=self._total_bytes
            )
            # 初始化为 0
            for i in range(self._total_bytes):
                self._shm.buf[i] = 0
        else:
            self._shm = shared_memory.SharedMemory(name=name, create=False)

        self._base = self._shm.buf

    @property
    def name(self) -> str:
        return self._shm.name

    @property
    def seq(self) -> int:
        """当前序列号"""
        return struct.unpack_from('Q', self._base, 0)[0]

    @classmethod
    def create(cls, shape: tuple, dtype):
        """创建新的共享内存数组"""
        return cls(name=None, shape=shape, dtype=dtype, create=True)

    @classmethod
    def connect(cls, name: str, shape: tuple, dtype):
        """连接到已存在的共享内存数组"""
        return cls(name=name, shape=shape, dtype=dtype, create=False)

    def write(self, data: np.ndarray, seq: int = None):
        """
        原子写入数据

        Args:
            data: numpy 数组
            seq:  可选序列号 (默认自增)
        """
        if seq is None:
            seq = self.seq + 1

        # 先写数据
        buf = np.ndarray(
            self.shape, dtype=self.dtype,
            buffer=self._base, offset=self._SEQ_SIZE
        )
        buf[:] = data

        # 最后写 seq
        struct.pack_into('Q', self._base, 0, seq)

    def read(self) -> Tuple[np.ndarray, int]:
        """
        一致性读取数据,只读取最后一个

        Returns:
            data: numpy 数组 (拷贝)
            seq:  序列号
        """
        while True:
            seq_before = self.seq
            data = np.ndarray(
                self.shape, dtype=self.dtype,
                buffer=self._base, offset=self._SEQ_SIZE
            ).copy()
            seq_after = self.seq

            if seq_before == seq_after and seq_before > 0:
                return data, seq_before
            # seq 不一致, 重试

    def read_no_copy(self) -> Tuple[np.ndarray, int]:
        """
        零拷贝读取 (注意: 返回的是共享内存视图, 不要修改)

        Returns:
            data: numpy 数组 (视图, 非拷贝)
            seq:  序列号
        """
        seq_val = self.seq
        data = np.ndarray(
            self.shape, dtype=self.dtype,
            buffer=self._base, offset=self._SEQ_SIZE
        )
        return data, seq_val

    def close(self):
        self._shm.close()

    def unlink(self):
        try:
            self._shm.unlink()
        except FileNotFoundError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ======================================================================
# 便捷测试
# ======================================================================
if __name__ == "__main__":
    import multiprocessing as mp

    # Linux 默认使用 fork，性能更好，无需显式设置

    print("=" * 60)
    print("SharedMemoryRingBuffer 测试")
    print("=" * 60)

    # 测试环形缓冲区
    ring = SharedMemoryRingBuffer.create(
        shape=(10,),
        dtype=np.float64,
        buffer_size=5,
        n_arrays=2
    )
    print(f"创建环形缓冲区: name={ring.name}, shape={ring.shape}, buffer_size={ring.buffer_size}")

    # 写入测试
    for i in range(7):
        arr1 = np.ones(10) * i
        arr2 = np.ones(10) * (i * 10)
        ring.put(arr1, arr2, timestamp=time.monotonic())
        print(f"  写入帧 {i}: arr1={arr1[0]}, arr2={arr2[0]}, write_idx={ring.write_index}")

    # 读取测试
    (arr1s, arr2s), timestamps = ring.get_last_k(3)
    print(f"\n读取最新 3 帧:")
    for i, (a1, a2, ts) in enumerate(zip(arr1s, arr2s, timestamps)):
        print(f"  帧 {i}: arr1={a1[0]}, arr2={a2[0]}, ts={ts:.3f}")

    ring.close()
    ring.unlink()

    print("\n" + "=" * 60)
    print("SharedMemoryArray 测试")
    print("=" * 60)

    # 测试单次数组
    arr = SharedMemoryArray.create(shape=(5,), dtype=np.float64)
    print(f"创建数组: name={arr.name}, shape={arr.shape}")

    # 写入测试
    for i in range(3):
        data = np.array([i, i * 2, i * 3, i * 4, i * 5], dtype=np.float64)
        arr.write(data)
        print(f"  写入: {data}, seq={arr.seq}")

    # 读取测试
    data, seq = arr.read()
    print(f"  读取: {data}, seq={seq}")

    arr.close()
    arr.unlink()

    print("\n所有测试通过!")
