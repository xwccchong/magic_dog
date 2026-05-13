#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器狗头部相机录制模块

架构:
- 使用子线程 (threading) 运行视频采集
- 主进程可以同时执行其他任务
- 采集线程通过 VideoClient.GetImageSample() API 获取 JPEG 图像

用法:
    recorder = FrontCameraRecorder(save_dir="/home/unitree/videos")
    recorder.start()

    # ... 运行其他任务 ...

    # 停止录制并保存视频
    recorder.stop()
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from typing import Optional, List

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

# ---- 必须在导入其他模块之前设置 DDS 环境变量 ----
os.environ["CYCLONEDDS_URI"] = '<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="eth0" priority="default" multicast="default" /></Interfaces></General></Domain></CycloneDDS>'
os.environ["RMW_IMPLEMENTATION"] = "rmw_cyclonedds_cpp"

sys.path.insert(0, '/home/unitree/unitree_sdk2_python')


# ======================================================================
# 视频采集线程
# ======================================================================
class VideoCaptureThread(threading.Thread):
    """
    视频采集线程

    持续调用 VideoClient.GetImageSample() 获取 JPEG 图像
    将图像帧存入帧列表
    """

    def __init__(
        self,
        frame_list: List,
        lock: threading.Lock,
        stop_event: threading.Event,
        target_fps: float = 10.0,
    ):
        """
        初始化采集线程

        Args:
            frame_list: 帧数据列表 (共享)
            lock: 线程锁
            stop_event: 停止信号
            target_fps: 目标帧率
        """
        super().__init__(daemon=True)
        self._frame_list = frame_list
        self._lock = lock
        self._stop_event = stop_event
        self._target_fps = target_fps
        self._frame_count = 0
        self._client = None

    def run(self):
        """线程主循环"""
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize
        from unitree_sdk2py.go2.video.video_client import VideoClient

        # 初始化 DDS
        ChannelFactoryInitialize(0, "eth0")

        # 初始化 VideoClient
        self._client = VideoClient()
        self._client.SetTimeout(5.0)
        self._client.Init()

        print("[VideoCaptureThread] 视频采集线程已启动")

        interval = 1.0 / self._target_fps

        while not self._stop_event.is_set():
            t0 = time.monotonic()

            try:
                code, data = self._client.GetImageSample()
                if code == 0 and len(data) > 0:
                    with self._lock:
                        self._frame_list.append(bytes(data))
                    self._frame_count += 1
            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"[VideoCaptureThread] 采集异常: {e}")

            # 控制帧率
            elapsed = time.monotonic() - t0
            if elapsed < interval:
                time.sleep(interval - elapsed)

        print(f"[VideoCaptureThread] 已停止, 共采集 {self._frame_count} 帧")

    @property
    def frame_count(self) -> int:
        return self._frame_count


# ======================================================================
# 主进程端 API
# ======================================================================
class FrontCameraRecorder:
    """
    机器狗头部相机录制器

    - 子线程持续采集视频帧
    - 主进程可以同时执行其他任务
    - 停止时将帧序列转换为 H.264 视频

    用法:
        with FrontCameraRecorder(save_dir="/path/to/videos") as recorder:
            time.sleep(60)  # 录制 60 秒，同时可以做其他事
        # 自动停止并保存
    """

    DEFAULT_FPS = 10

    def __init__(
        self,
        save_dir: str = "/home/unitree/videos",
        fps: float = DEFAULT_FPS,
    ):
        """
        初始化录制器

        Args:
            save_dir: 视频保存目录
            fps: 目标帧率
        """
        self._save_dir = save_dir
        self._fps = fps

        # 帧数据存储
        self._frame_list: List[bytes] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._capture_thread: Optional[VideoCaptureThread] = None

        self._save_path: Optional[str] = None
        self._start_time: Optional[float] = None

    # ---- context manager ----
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    # ---- 生命周期 ----
    def start(self):
        """启动录制"""
        if self._capture_thread is not None and self._capture_thread.is_alive():
            print("[FrontCameraRecorder] 录制线程已在运行")
            return

        # 创建保存目录
        os.makedirs(self._save_dir, exist_ok=True)

        # 清理状态
        self._frame_list.clear()
        self._stop_event.clear()
        self._start_time = time.time()

        # 启动采集线程
        self._capture_thread = VideoCaptureThread(
            frame_list=self._frame_list,
            lock=self._lock,
            stop_event=self._stop_event,
            target_fps=self._fps,
        )
        self._capture_thread.start()

        # 等待线程启动
        time.sleep(0.5)

        print(f"[FrontCameraRecorder] 已启动, 帧率: {self._fps} fps")

    def stop(self):
        """停止录制并保存视频"""
        print("[FrontCameraRecorder] 正在停止...")

        # 停止采集线程
        self._stop_event.set()

        if self._capture_thread is not None:
            self._capture_thread.join(timeout=5.0)
            self._capture_thread = None

        # 保存视频
        self._save_video()

        duration = time.time() - self._start_time if self._start_time else 0
        print(f"[FrontCameraRecorder] 已停止")
        print(f"  时长: {duration:.2f}s")
        if self._save_path:
            file_size = os.path.getsize(self._save_path) / (1024 * 1024)
            print(f"  保存路径: {self._save_path}")
            print(f"  文件大小: {file_size:.2f} MB")

    def _save_video(self):
        """将帧序列保存为视频"""
        if len(self._frame_list) == 0:
            print("[FrontCameraRecorder] 无帧数据, 无法保存")
            return

        # 生成保存文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._save_path = os.path.join(
            self._save_dir,
            f"front_camera_{timestamp}.mp4"
        )

        # 创建临时目录存放帧图片
        frames_dir = os.path.join(self._save_dir, f"_frames_{timestamp}")
        os.makedirs(frames_dir, exist_ok=True)

        # 保存帧图片
        frame_count = 0
        with self._lock:
            for i, frame_data in enumerate(self._frame_list):
                frame_path = os.path.join(frames_dir, f"frame_{i:05d}.jpg")
                with open(frame_path, 'wb') as f:
                    f.write(frame_data)
                frame_count += 1

        print(f"[FrontCameraRecorder] 已保存 {frame_count} 帧图片")

        # 使用 ffmpeg 转换为 H.264 视频
        result = subprocess.run([
            'ffmpeg', '-y',
            '-framerate', str(self._fps),
            '-i', os.path.join(frames_dir, 'frame_%05d.jpg'),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            self._save_path
        ], capture_output=True, text=True)

        # 清理临时帧目录
        import shutil
        shutil.rmtree(frames_dir)

        if result.returncode != 0:
            print(f"[FrontCameraRecorder] 视频转换失败: {result.stderr}")
            self._save_path = None
        else:
            print(f"[FrontCameraRecorder] 视频已生成")

    @property
    def is_recording(self) -> bool:
        """是否正在录制"""
        return self._capture_thread is not None and self._capture_thread.is_alive()

    @property
    def save_path(self) -> Optional[str]:
        """视频保存路径"""
        return self._save_path

    @property
    def frame_count(self) -> int:
        """已采集的帧数"""
        if self._capture_thread:
            return self._capture_thread.frame_count
        return len(self._frame_list)

    def get_latest_frame(self) -> Optional[bytes]:
        """
        获取最新一帧 (JPEG 格式)

        Returns:
            JPEG 数据, 或 None 如果无数据
        """
        with self._lock:
            if len(self._frame_list) > 0:
                return self._frame_list[-1]
        return None


# ======================================================================
# 测试入口
# ======================================================================
if __name__ == "__main__":
    print("--- 机器狗头部相机录制测试 (子线程版本) ---")
    print("按 Ctrl+C 停止录制\n")

    recorder = FrontCameraRecorder(
        save_dir="/home/unitree/unitree_sdk2_python/agent/test/videos",
        fps=10,
    )

    try:
        recorder.start()
        print("正在录制... (按 Ctrl+C 停止)\n")

        # 主进程可以同时做其他事情
        while recorder.is_recording:
            time.sleep(1.0)
            elapsed = time.time() - recorder._start_time
            print(f"  录制中... {elapsed:.0f}s, {recorder.frame_count} 帧", end='\r')

    except KeyboardInterrupt:
        print("\n\n收到停止信号...")

    finally:
        recorder.stop()
        print("\n录制完成!")

        if recorder.save_path:
            print(f"\n播放命令:")
            print(f"  ffplay {recorder.save_path}")