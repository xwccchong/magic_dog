#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RealSense 相机多进程采集模块

架构 (参考 diffusion_policy SingleRealsense):
- 采集进程: 独立 mp.Process, 持续从 RealSense 采集帧, 写入共享内存环形缓冲区
- 主进程: 通过共享内存零拷贝读取最新帧

与 realsense.py (多线程版) 的区别:
  - 相机硬件 I/O 完全隔离在子进程, 不会阻塞主进程 GIL
  - 使用 multiprocessing.shared_memory 实现 true 零拷贝
  - 适合与其他 CPU 密集任务 (推理/规划) 并行运行
  - Linux 系统使用 fork 模式，性能更优

用法:
    cam = RealSenseSubProcess(fps=30)
    cam.start()

    # 获取最新 1 帧
    rgbs, depths, size_info = cam.get_images(num_frames=1)

    # 用完关闭
    cam.stop()
"""

import time
import multiprocessing as mp
import numpy as np
from typing import Optional

try:
    import pyrealsense2 as rs
except ImportError:
    rs = None

from .shared_memory_buffer import SharedMemoryRingBuffer, SharedMemoryArray


# ======================================================================
# 子进程入口: 持续采集循环
# ======================================================================
def _capture_worker(
    rgb_shm_name: str,
    depth_shm_name: str,
    buffer_size: int,
    width: int,
    height: int,
    fps: int,
    stop_event: mp.Event,
    ready_event: mp.Event,
    intrinsics_shm_name: str,
    error_queue: mp.Queue,
):
    """子进程入口函数, 持续从 RealSense 采集并写入共享内存"""
    import cv2
    cv2.setNumThreads(1)

    try:
        # 连接到 RGB 环形缓冲区: (H, W, 3) uint8
        rgb_ring = SharedMemoryRingBuffer.connect(
            name=rgb_shm_name,
            shape=(height, width, 3),
            dtype=np.uint8,
            buffer_size=buffer_size,
            n_arrays=1,
        )

        # 连接到 Depth 环形缓冲区: (H, W) uint16
        depth_ring = SharedMemoryRingBuffer.connect(
            name=depth_shm_name,
            shape=(height, width),
            dtype=np.uint16,
            buffer_size=buffer_size,
            n_arrays=1,
        )

        # 连接到内参共享数组
        intrinsics_arr = SharedMemoryArray.connect(
            name=intrinsics_shm_name,
            shape=(7,),
            dtype=np.float64,
        )

        # 初始化 RealSense pipeline
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        align = rs.align(rs.stream.color)

        # 启动相机的数据流
        profile = pipeline.start(config)
        print(">>> 视觉系统初始化完成")

        # 启用 global time 提高时间戳精度
        try:
            sensor = profile.get_device().first_color_sensor()
            sensor.set_option(rs.option.global_time_enabled, 1)
        except Exception:
            pass

        # 写入内参到共享数组: [fx, fy, cx, cy, height, width, depth_scale]
        color_stream = profile.get_stream(rs.stream.color)
        intr = color_stream.as_video_stream_profile().get_intrinsics()
        intr_data = np.array([
            intr.fx,
            intr.fy,
            intr.ppx,
            intr.ppy,
            float(intr.height),
            float(intr.width),
            0.001,  # depth_scale placeholder
        ], dtype=np.float64)

        # 获取深度 scale
        try:
            depth_sensor = profile.get_device().first_depth_sensor()
            intr_data[6] = depth_sensor.get_depth_scale()
        except Exception:
            intr_data[6] = 0.001  # D400 默认 ~0.001

        intrinsics_arr.write(intr_data)

        # 丢弃前几帧让曝光稳定
        for _ in range(10):
            pipeline.wait_for_frames()

        # 通知主进程: 就绪
        ready_event.set()

        interval = 1.0 / fps
        while not stop_event.is_set():
            t0 = time.monotonic()
            try:
                frames = pipeline.wait_for_frames()
                frames = align.process(frames)

                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()
                if color_frame is None or depth_frame is None:
                    continue

                color_img = np.asarray(color_frame.get_data())
                depth_img = np.asarray(depth_frame.get_data())
                ts = time.monotonic()

                # 分别写入各自的环形缓冲区
                rgb_ring.put(color_img, timestamp=ts)
                depth_ring.put(depth_img, timestamp=ts)

            except Exception as e:
                if not stop_event.is_set():
                    print(f"[RealSense-SubProcess] 采集异常: {e}")
                continue

            elapsed = time.monotonic() - t0
            if elapsed < interval:
                time.sleep(interval - elapsed)

    except Exception as e:
        # 初始化失败: 把错误发回主进程
        error_queue.put(e)
        return
    finally:
        try:
            pipeline.stop()
        except Exception:
            pass
        try:
            rgb_ring.close()
        except Exception:
            pass
        try:
            depth_ring.close()
        except Exception:
            pass
        try:
            intrinsics_arr.close()
        except Exception:
            pass


# ======================================================================
# 主进程端 API
# ======================================================================
class RealSenseSubProcess:
    """
    RealSense 相机多进程封装

    - 子进程独立采集, 写入共享内存环形缓冲区
    - 主进程零拷贝读取最新帧
    - 支持 context manager

    用法:
        with RealSenseSubProcess(fps=30) as cam:
            rgbs, depths, info = cam.get_images(num_frames=1)
    """

    DEFAULT_BUFFER_SIZE = 150  # ~5s @ 30Hz

    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
    ):
        self._width = width
        self._height = height
        self._fps = fps
        self._buffer_size = buffer_size

        # RGB 环形缓冲区: (H, W, 3) uint8
        self._rgb_ring = SharedMemoryRingBuffer.create(
            shape=(height, width, 3),
            dtype=np.uint8,
            buffer_size=buffer_size,
            n_arrays=1,
        )

        # Depth 环形缓冲区: (H, W) uint16
        self._depth_ring = SharedMemoryRingBuffer.create(
            shape=(height, width),
            dtype=np.uint16,
            buffer_size=buffer_size,
            n_arrays=1,
        )

        # 内参共享数组: [fx, fy, cx, cy, height, width, depth_scale]
        self._intrinsics_arr = SharedMemoryArray.create(
            shape=(7,),
            dtype=np.float64,
        )

        # 进程间同步
        self._stop_event = mp.Event()
        self._ready_event = mp.Event()
        self._error_queue = mp.Queue()
        self._process: Optional[mp.Process] = None

    # ---- context manager ----
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    # ---- 生命周期 ----
    def start(self, wait=True, timeout=10.0):
        """启动采集子进程"""
        if self._process is not None and self._process.is_alive():
            print("[RealSense-SubProcess] 采集进程已在运行")
            return

        self._stop_event.clear()
        self._ready_event.clear()

        # 清空残留错误
        while not self._error_queue.empty():
            self._error_queue.get()

        self._process = mp.Process(
            target=_capture_worker,
            args=(
                self._rgb_ring.name,
                self._depth_ring.name,
                self._buffer_size,
                self._width,
                self._height,
                self._fps,
                self._stop_event,
                self._ready_event,
                self._intrinsics_arr.name,
                self._error_queue,
            ),
            daemon=True,
        )
        self._process.start()

        if wait:
            if not self._ready_event.wait(timeout=timeout):
                # 检查子进程是否报告了初始化错误
                if not self._error_queue.empty():
                    err = self._error_queue.get()
                    raise RuntimeError(
                        f"[RealSense-SubProcess] 子进程初始化失败: {err}"
                    ) from err
                raise TimeoutError(
                    f"[RealSense-SubProcess] 子进程未在 {timeout}s 内就绪, 可能初始化失败"
                )

        print(f"[RealSense-SubProcess] 已启动 ({self._width}x{self._height} @ {self._fps}Hz)")

    def stop(self, wait=True):
        """停止采集子进程并释放共享内存"""
        self._stop_event.set()

        if self._process is not None:
            if wait:
                self._process.join(timeout=5.0)
                if self._process.is_alive():
                    self._process.kill()
                    self._process.join(timeout=2.0)
            self._process = None

        # 释放共享内存
        self._rgb_ring.close()
        self._rgb_ring.unlink()
        self._depth_ring.close()
        self._depth_ring.unlink()
        self._intrinsics_arr.close()
        self._intrinsics_arr.unlink()

        print("[RealSense-SubProcess] 已停止, 资源已释放")

    @property
    def is_ready(self) -> bool:
        return self._ready_event.is_set()

    # ---- 数据读取 ----
    def get_images(self, num_frames: int = 1):
        """
        获取最新 num_frames 帧

        Args:
            num_frames: 需要获取的帧数 (从最新帧往回取)

        Returns:
            rgbs:      list[np.ndarray] — shape (H, W, 3), dtype uint8
            depths:    list[np.ndarray] — shape (H, W), dtype uint16 (毫米)
            size_info: dict — 含 height/width/channels + 相机内参
        """
        rgbs, _ = self._rgb_ring.get_last_k(num_frames)
        depths, _ = self._depth_ring.get_last_k(num_frames)
        return rgbs, depths, self.get_image_size()

    def get_image_size(self) -> dict:
        """
        返回图像尺寸与相机内参 (子进程写入后才有有效值)

        Returns:
            dict: {'height', 'width', 'channels', 'fx', 'fy', 'cx', 'cy', 'depth_scale'}
        """
        v, _ = self._intrinsics_arr.read()
        return {
            "height": int(v[4]) if v[4] > 0 else self._height,
            "width": int(v[5]) if v[5] > 0 else self._width,
            "channels": 3,
            "fx": float(v[0]),
            "fy": float(v[1]),
            "cx": float(v[2]),
            "cy": float(v[3]),
            "depth_scale": float(v[6]),
        }

    def get_intrinsics_matrix(self) -> np.ndarray:
        """返回 3x3 相机内参矩阵"""
        v, _ = self._intrinsics_arr.read()
        mat = np.eye(3)
        mat[0, 0] = v[0]
        mat[1, 1] = v[1]
        mat[0, 2] = v[2]
        mat[1, 2] = v[3]
        return mat

    def get_depth_scale(self) -> float:
        """返回深度 scale (深度值 * scale = 米)"""
        v, _ = self._intrinsics_arr.read()
        return float(v[6])

    def buffer_count(self) -> int:
        """当前缓冲区中可用的帧数"""
        return self._rgb_ring.count


# ======================================================================
# 便捷入口
# ======================================================================
if __name__ == "__main__":
    # Linux 默认使用 fork，无需显式设置

    print("--- RealSense 多进程采集测试 ---")
    cam = RealSenseSubProcess(fps=30) # 初始化子进程

    cam.start() # 启动子进程

    import cv2
    import os

    save_dir = "/home/unitree/unitree_sdk2_python/agent/test"
    os.makedirs(save_dir, exist_ok=True)

    last_rgb = None
    last_depth = None

    try:
        for i in range(5):
            time.sleep(1.0)
            rgbs, depths, info = cam.get_images(num_frames=1)
            if len(rgbs) > 0:
                print(
                    f"[{i+1}] color: {rgbs[0].shape}, "
                    f"depth: {depths[0].shape}, "
                    f"info: {info}"
                )
                last_rgb = rgbs[-1]
                last_depth = depths[-1]
            else:
                print(f"[{i+1}] 无数据")
    finally:
        cam.stop()

    # 保存最后一帧
    if last_rgb is not None:
        cv2.imwrite(os.path.join(save_dir, "last_rgb.png"), last_rgb)

        # 深度图伪彩色可视化
        depth_vis = last_depth.astype(np.float32)
        depth_vis = cv2.normalize(depth_vis, None, 0, 255, cv2.NORM_MINMAX)
        depth_vis = depth_vis.astype(np.uint8)
        depth_color = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)

        # 0 值 (无深度) 标记为黑色
        zero_mask = last_depth == 0
        depth_color[zero_mask] = [0, 0, 0]

        cv2.imwrite(os.path.join(save_dir, "last_depth.png"), depth_color)
        print(f"已保存到 {save_dir}")
        print(f"  RGB:   last_rgb.png   shape={last_rgb.shape}")
        print(f"  Depth: last_depth.png shape={last_depth.shape}  "
              f"range=[{last_depth.min()}, {last_depth.max()}]")
    else:
        print("未采集到任何帧, 无法保存")
