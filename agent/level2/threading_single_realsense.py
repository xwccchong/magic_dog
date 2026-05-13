#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RealSense 相机采集模块
- 后台线程持续采集 RGB + 深度图 (默认 30Hz)
- 线程安全环形缓冲区存储最新帧
- 提供 get_images() 接口供外部进程按需获取指定数量的图像

用法:
    from level2.realsense import RealSenseCamera

    cam = RealSenseCamera(fps=30)
    # ... 采集自动在后台运行 ...

    # 获取最新 1 帧
    rgbs, depths, size_info = cam.get_images(num_frames=1)
    # rgbs: list[np.ndarray]  (H, W, 3) uint8
    # depths: list[np.ndarray] (H, W)    uint16 (单位 mm)
    # size_info: dict {'height': H, 'width': W, 'channels': 3}

    # 用完关闭
    cam.stop()
"""

import threading
import time
from collections import deque
from typing import Optional

import numpy as np
import pyrealsense2 as rs


class RealSenseCamera:
    """RealSense 相机封装: 后台采集 + 线程安全读取"""

    # 默认缓冲区容量 (保留最近 90 帧 ≈ 3s @ 30Hz)
    DEFAULT_BUFFER_SIZE = 90

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        align_depth_to_color: bool = True,
    ):
        """
        Args:
            width:       图像宽度
            height:      图像高度
            fps:         目标采集帧率 (Hz)
            buffer_size: 环形缓冲区最大帧数
            align_depth_to_color: 是否将深度图对齐到彩色图
        """
        self._width = width
        self._height = height
        self._fps = fps
        self._align_depth = align_depth_to_color

        # ---- RealSense pipeline 初始化 ----
        self._pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        if align_depth_to_color:
            self._align = rs.align(rs.stream.color)
        else:
            self._align = None
        self._profile = self._pipeline.start(config)

        # 获取相机内参
        color_stream = self._profile.get_stream(rs.stream.color)
        self._intrinsics = color_stream.as_video_stream_profile().get_intrinsics()

        # ---- 帧缓冲区 (线程安全) ----
        self._buffer: deque = deque(maxlen=buffer_size)
        self._lock = threading.Lock()

        # ---- 后台采集线程 ----
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._start_capture()

    # ------------------------------------------------------------------
    # 内部: 后台采集
    # ------------------------------------------------------------------
    def _start_capture(self):
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        print(f"[RealSense] 后台采集已启动 ({self._width}x{self._height} @ {self._fps}Hz)")

    def _capture_loop(self):
        """持续采集循环, 按 fps 控制速率"""
        interval = 1.0 / self._fps
        while self._running:
            t0 = time.monotonic()
            try:
                frames = self._pipeline.wait_for_frames()
                if self._align is not None:
                    frames = self._align.process(frames)

                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()
                if color_frame is None or depth_frame is None:
                    continue

                color_img = np.asanyarray(color_frame.get_data()).copy()
                depth_img = np.asanyarray(depth_frame.get_data()).copy()

                with self._lock:
                    self._buffer.append((color_img, depth_img, time.monotonic()))

            except Exception as e:
                if self._running:
                    print(f"[RealSense] 采集异常: {e}")
                continue

            # 简单帧率控制: 若 pipeline 实际输出快于目标 fps, 适当 sleep
            elapsed = time.monotonic() - t0
            if elapsed < interval:
                time.sleep(interval - elapsed)

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------
    def get_images(self, num_frames: int = 1):
        """
        获取缓冲区中最新 num_frames 帧图像

        Args:
            num_frames: 需要获取的帧数 (从最新帧往回取)

        Returns:
            rgbs:      list[np.ndarray] — RGB 图列表, 每张 shape (H, W, 3), dtype uint8
            depths:    list[np.ndarray] — 深度图列表, 每张 shape (H, W),    dtype uint16 (单位: 毫米)
            size_info: dict — {'height': H, 'width': W, 'channels': 3,
                               'fx': fx, 'fy': fy, 'cx': cx, 'cy': cy}
        """
        with self._lock:
            buf_list = list(self._buffer)

        available = len(buf_list)
        n = min(num_frames, available)
        if n == 0:
            print("[RealSense] 警告: 缓冲区为空, 暂无可用帧")
            return [], [], self.get_image_size()

        selected = buf_list[-n:]  # 取最新 n 帧

        rgbs = [item[0] for item in selected]
        depths = [item[1] for item in selected]
        timestamps = [item[2] for item in selected]

        return rgbs, depths, self.get_image_size()

    def get_image_size(self) -> dict:
        """
        返回图像尺寸与相机内参

        Returns:
            dict: {'height': H, 'width': W, 'channels': 3,
                   'fx': ..., 'fy': ..., 'cx': ..., 'cy': ...}
        """
        return {
            "height": self._height,
            "width": self._width,
            "channels": 3,
            "fx": self._intrinsics.fx,
            "fy": self._intrinsics.fy,
            "cx": self._intrinsics.ppx,
            "cy": self._intrinsics.ppy,
        }

    def buffer_count(self) -> int:
        """当前缓冲区中的帧数"""
        with self._lock:
            return len(self._buffer)

    def stop(self):
        """停止采集并释放资源"""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None
        try:
            self._pipeline.stop()
        except Exception:
            pass
        print("[RealSense] 已停止采集, 资源已释放")

    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass


# ------------------------------------------------------------------
# 便捷函数: 直接获取单帧 (适用于简单场景)
# ------------------------------------------------------------------
def capture_one_frame(width: int = 1280, height: int = 720):
    """
    不需要启动后台线程, 直接拍摄一帧并返回

    Returns:
        rgb, depth, size_info
        如果失败返回 None, None, None
    """
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
    align = rs.align(rs.stream.color)

    try:
        profile = pipeline.start(config)
        # 丢弃前几帧让曝光稳定
        for _ in range(10):
            pipeline.wait_for_frames()

        frames = pipeline.wait_for_frames()
        aligned = align.process(frames)
        color_frame = aligned.get_color_frame()
        depth_frame = aligned.get_depth_frame()

        if color_frame is None or depth_frame is None:
            return None, None, None

        color_img = np.asanyarray(color_frame.get_data()).copy()
        depth_img = np.asanyarray(depth_frame.get_data()).copy()

        intrinsics = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        size_info = {
            "height": height,
            "width": width,
            "channels": 3,
            "fx": intrinsics.fx,
            "fy": intrinsics.fy,
            "cx": intrinsics.ppx,
            "cy": intrinsics.ppy,
        }

        return color_img, depth_img, size_info
    except Exception as e:
        print(f"[RealSense] capture_one_frame 异常: {e}")
        return None, None, None
    finally:
        try:
            pipeline.stop()
        except Exception:
            pass
