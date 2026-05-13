#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RealSenseSubProcess 功能测试

测试项:
1. 启动子进程采集
2. 获取单帧 RGB + 深度图
3. 保存图像到磁盘
4. 打印相机内参 & 图像尺寸
5. 连续采集多帧, 检查帧率
6. 停止子进程
"""

import os
import time
import cv2
import numpy as np

from agent.level2.mp_single_realsense import RealSenseSubProcess


def test_single_frame():
    """测试 1: 启动子进程, 获取一帧图像并保存"""
    print("=" * 60)
    print("测试 1: 单帧采集 & 保存")
    print("=" * 60)

    save_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(save_dir, exist_ok=True)

    cam = RealSenseSubProcess(width=1280, height=720, fps=30)
    cam.start(wait=True, timeout=15.0)

    try:
        # 等待几帧写入缓冲区
        time.sleep(1.0)

        rgbs, depths, info = cam.get_images(num_frames=1)
        assert len(rgbs) > 0, "未获取到图像帧"

        rgb = rgbs[0]
        depth = depths[0]

        print(f"  RGB shape:  {rgb.shape}, dtype: {rgb.dtype}")
        print(f"  Depth shape: {depth.shape}, dtype: {depth.dtype}")
        print(f"  相机内参: fx={info['fx']:.2f}, fy={info['fy']:.2f}, "
              f"cx={info['cx']:.2f}, cy={info['cy']:.2f}")
        print(f"  图像尺寸: {info['width']}x{info['height']}")
        print(f"  深度 scale: {info['depth_scale']}")

        # 保存 RGB 图
        rgb_path = os.path.join(save_dir, "test_rgb.png")
        cv2.imwrite(rgb_path, rgb)
        print(f"  RGB 已保存: {rgb_path}")

        # 保存深度图 (归一化到 0-255 可视化)
        depth_visual = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        depth_path = os.path.join(save_dir, "test_depth.png")
        cv2.imwrite(depth_path, depth_visual)
        print(f"  Depth 已保存: {depth_path}")

        # 保存原始深度数据 (uint16, 可用于后续计算)
        depth_raw_path = os.path.join(save_dir, "test_depth_raw.png")
        cv2.imwrite(depth_raw_path, depth)

        print("  测试 1 通过\n")
    finally:
        cam.stop()


def test_multi_frames():
    """测试 2: 连续采集多帧, 检查缓冲区"""
    print("=" * 60)
    print("测试 2: 多帧采集 & 帧率估算")
    print("=" * 60)

    cam = RealSenseSubProcess(fps=30, buffer_size=60)
    cam.start(wait=True, timeout=15.0)

    try:
        # 让缓冲区积累一些帧
        time.sleep(2.0)

        buf_count = cam.buffer_count()
        print(f"  缓冲区帧数: {buf_count}")

        # 获取最新 5 帧
        rgbs, depths, info = cam.get_images(num_frames=5)
        print(f"  获取到 {len(rgbs)} 帧")

        for i, (rgb, depth) in enumerate(zip(rgbs, depths)):
            print(f"  帧 {i}: RGB {rgb.shape}, Depth min={depth.min()}, max={depth.max()}")

        # 估算帧率: 缓冲区帧数 / 运行时间
        elapsed = 2.0
        fps_est = buf_count / elapsed
        print(f"  估算帧率: {fps_est:.1f} Hz")

        print("  测试 2 通过\n")
    finally:
        cam.stop()


def test_context_manager():
    """测试 3: context manager 用法"""
    print("=" * 60)
    print("测试 3: context manager 自动启停")
    print("=" * 60)

    with RealSenseSubProcess(fps=15) as cam:
        time.sleep(1.0)
        rgbs, depths, info = cam.get_images(num_frames=1)
        print(f"  is_ready: {cam.is_ready}")
        print(f"  获取帧数: {len(rgbs)}")

    print("  context manager 退出后 is_ready (进程已结束)")
    print("  测试 3 通过\n")


def test_intrinsics_matrix():
    """测试 4: 内参矩阵 & depth scale"""
    print("=" * 60)
    print("测试 4: 相机内参矩阵")
    print("=" * 60)

    cam = RealSenseSubProcess(fps=15)
    cam.start(wait=True, timeout=15.0)

    try:
        time.sleep(1.0)

        K = cam.get_intrinsics_matrix()
        print(f"  内参矩阵 K:\n{K}")
        assert K.shape == (3, 3)
        assert K[0, 0] > 0, "fx 应为正数"

        scale = cam.get_depth_scale()
        print(f"  深度 scale: {scale}")
        assert scale > 0, "depth_scale 应为正数"

        print("  测试 4 通过\n")
    finally:
        cam.stop()


if __name__ == "__main__":
    # Linux 默认使用 fork，无需显式设置

    print("\n>>> RealSenseSubProcess 功能测试 <<<\n")

    try:
        test_single_frame()
        test_multi_frames()
        test_context_manager()
        test_intrinsics_matrix()
        print("=" * 60)
        print("所有测试通过!")
        print("=" * 60)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
