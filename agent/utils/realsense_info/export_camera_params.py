#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RealSense 相机参数导出工具

导出内容:
- 内参 (Intrinsics): fx, fy, cx, cy
- 畸变系数 (Distortion): k1, k2, p1, p2, k3
- 外参 (Extrinsics): Depth <-> Color 变换矩阵
- 深度参数: depth_scale, depth_unit

用法:
    python export_camera_params.py
    python export_camera_params.py --output camera_params.json
    python export_camera_params.py --yaml camera_params.yaml
"""

import os
import sys
import json
import argparse
import numpy as np
from datetime import datetime

try:
    import pyrealsense2 as rs
except ImportError:
    print("❌ 请安装 pyrealsense2: pip install pyrealsense2")
    sys.exit(1)


def get_device_info(device):
    """获取设备信息"""
    return {
        "name": device.get_info(rs.camera_info.name),
        "serial": device.get_info(rs.camera_info.serial_number),
        "firmware": device.get_info(rs.camera_info.firmware_version),
        "usb_type": device.get_info(rs.camera_info.usb_type_descriptor),
    }


def get_intrinsics(video_stream_profile):
    """从视频流配置获取内参"""
    intr = video_stream_profile.as_video_stream_profile().get_intrinsics()

    return {
        "width": intr.width,
        "height": intr.height,
        "fx": float(intr.fx),
        "fy": float(intr.fy),
        "cx": float(intr.ppx),  # ppx = principal point x = cx
        "cy": float(intr.ppy),  # ppy = principal point y = cy
        "distortion_model": str(intr.model).split('.')[-1],
        "coeffs": [float(c) for c in intr.coeffs],
    }


def intrinsics_to_matrix(intr_dict):
    """内参字典转 3x3 矩阵"""
    return np.array([
        [intr_dict["fx"], 0, intr_dict["cx"]],
        [0, intr_dict["fy"], intr_dict["cy"]],
        [0, 0, 1]
    ], dtype=np.float64)


def get_extrinsics(from_stream, to_stream):
    """获取两个流之间的外参"""
    extr = from_stream.get_extrinsics_to(to_stream)

    rotation = np.array(extr.rotation, dtype=np.float64).reshape(3, 3)
    translation = np.array(extr.translation, dtype=np.float64)

    # 构建 4x4 齐次变换矩阵
    transform = np.eye(4, dtype=np.float64)
    transform[:3, :3] = rotation
    transform[:3, 3] = translation

    return {
        "rotation": rotation.tolist(),
        "translation": translation.tolist(),
        "transform_matrix": transform.tolist(),
    }


def get_supported_resolutions(device):
    """获取设备支持的分辨率"""
    resolutions = {}

    for sensor in device.sensors:
        sensor_name = sensor.get_info(rs.camera_info.name)
        resolutions[sensor_name] = []

        for profile in sensor.profiles:
            if profile.stream_type() in [rs.stream.depth, rs.stream.color]:
                vp = profile.as_video_stream_profile()
                resolutions[sensor_name].append({
                    "stream": str(profile.stream_type()).split('.')[-1],
                    "width": vp.width(),
                    "height": vp.height(),
                    "fps": vp.fps(),
                    "format": str(vp.format()).split('.')[-1],
                })

    return resolutions


def find_common_resolution(device, preferred_width=640, preferred_height=480, preferred_fps=30):
    """查找深度和彩色流都支持的分辨率"""
    depth_resolutions = []
    color_resolutions = []

    for sensor in device.sensors:
        for profile in sensor.profiles:
            vp = profile.as_video_stream_profile()
            res = (vp.width(), vp.height(), vp.fps())

            if profile.stream_type() == rs.stream.depth:
                if res not in depth_resolutions:
                    depth_resolutions.append(res)
            elif profile.stream_type() == rs.stream.color:
                if res not in color_resolutions:
                    color_resolutions.append(res)

    # 找到两者都支持的分辨率
    common = set(depth_resolutions) & set(color_resolutions)

    if not common:
        # 如果没有共同分辨率，返回默认值
        return 640, 480, 15

    # 按优先级排序：优先选择接近 preferred 的分辨率
    def score(res):
        w, h, f = res
        # 距离 preferred 的差异
        diff = abs(w - preferred_width) + abs(h - preferred_height) + abs(f - preferred_fps) * 10
        return diff

    sorted_common = sorted(common, key=score)
    best = sorted_common[0]

    return best


def export_camera_params(width=None, height=None, fps=None):
    """导出相机参数"""
    print("=" * 60)
    print("RealSense 相机参数导出")
    print("=" * 60)

    # 创建上下文和设备
    ctx = rs.context()
    devices = ctx.query_devices()

    if len(devices) == 0:
        print("❌ 未检测到 RealSense 相机")
        return None

    device = devices[0]
    device_info = get_device_info(device)
    print(f"📷 设备: {device_info['name']}")
    print(f"   序列号: {device_info['serial']}")
    print(f"   固件: {device_info['firmware']}")

    # 如果未指定分辨率，自动查找支持的分辨率
    if width is None or height is None or fps is None:
        width, height, fps = find_common_resolution(device)
        print(f"   自动选择分辨率: {width}x{height}@{fps}fps")

    # 创建 pipeline
    pipeline = rs.pipeline()
    config = rs.config()

    # 配置流
    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)

    # 启动
    try:
        profile = pipeline.start(config)
    except RuntimeError as e:
        print(f"❌ 不支持的分辨率配置: {width}x{height}@{fps}fps")
        print("   尝试使用默认配置...")

        # 尝试默认配置
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
        profile = pipeline.start(config)
        width, height, fps = 640, 480, 15

    # 获取流配置
    depth_stream = profile.get_stream(rs.stream.depth)
    color_stream = profile.get_stream(rs.stream.color)

    # 获取深度传感器参数
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    depth_unit = 1.0 / depth_scale  # 米/单位

    # 获取内参
    depth_intr = get_intrinsics(depth_stream)
    color_intr = get_intrinsics(color_stream)

    # 获取外参 (Depth -> Color)
    depth_to_color = get_extrinsics(depth_stream, color_stream)
    color_to_depth = get_extrinsics(color_stream, depth_stream)

    # 停止 pipeline
    pipeline.stop()

    # 组装结果
    result = {
        "export_time": datetime.now().isoformat(),
        "device": device_info,
        "config": {
            "width": width,
            "height": height,
            "fps": fps,
        },
        "depth": {
            "intrinsics": depth_intr,
            "intrinsics_matrix": intrinsics_to_matrix(depth_intr).tolist(),
            "depth_scale": depth_scale,
            "depth_unit_m": depth_unit,
        },
        "color": {
            "intrinsics": color_intr,
            "intrinsics_matrix": intrinsics_to_matrix(color_intr).tolist(),
        },
        "extrinsics": {
            "depth_to_color": depth_to_color,
            "color_to_depth": color_to_depth,
        },
    }

    # 打印摘要
    print("\n📊 内参摘要:")
    print("-" * 40)
    print(f"  Depth: {depth_intr['width']}x{depth_intr['height']}")
    print(f"    fx={depth_intr['fx']:.2f}, fy={depth_intr['fy']:.2f}")
    print(f"    cx={depth_intr['cx']:.2f}, cy={depth_intr['cy']:.2f}")
    print(f"  Color: {color_intr['width']}x{color_intr['height']}")
    print(f"    fx={color_intr['fx']:.2f}, fy={color_intr['fy']:.2f}")
    print(f"    cx={color_intr['cx']:.2f}, cy={color_intr['cy']:.2f}")

    print("\n📐 深度参数:")
    print("-" * 40)
    print(f"  depth_scale: {depth_scale} ({depth_unit:.6f} m/unit)")

    print("\n🔄 外参 (Depth -> Color):")
    print("-" * 40)
    print(f"  Translation: [{depth_to_color['translation'][0]:.4f}, "
          f"{depth_to_color['translation'][1]:.4f}, "
          f"{depth_to_color['translation'][2]:.4f}] m")

    return result


def save_json(data, filepath):
    """保存为 JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 已保存: {filepath}")


def save_yaml(data, filepath):
    """保存为 YAML"""
    try:
        import yaml
    except ImportError:
        print("❌ 请安装 pyyaml: pip install pyyaml")
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    print(f"\n✅ 已保存: {filepath}")


def save_opencv_format(data, filepath):
    """
    保存为 OpenCV 格式的配置文件
    可用于 cv2.undistort() 等函数
    """
    # Depth 内参
    depth_K = np.array(data["depth"]["intrinsics_matrix"])
    depth_D = np.array(data["depth"]["intrinsics"]["coeffs"])

    # Color 内参
    color_K = np.array(data["color"]["intrinsics_matrix"])
    color_D = np.array(data["color"]["intrinsics"]["coeffs"])

    # 外参
    R = np.array(data["extrinsics"]["depth_to_color"]["rotation"])
    T = np.array(data["extrinsics"]["depth_to_color"]["translation"])

    opencv_data = {
        "camera_matrix": color_K.tolist(),
        "distortion_coefficients": color_D.tolist(),
        "image_width": data["config"]["width"],
        "image_height": data["config"]["height"],
        "depth_to_color": {
            "R": R.tolist(),
            "T": T.tolist(),
        },
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(opencv_data, f, indent=2)
    print(f"\n✅ OpenCV 格式已保存: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="RealSense 相机参数导出")
    parser.add_argument("--width", type=int, default=None, help="图像宽度 (不指定则自动选择)")
    parser.add_argument("--height", type=int, default=None, help="图像高度 (不指定则自动选择)")
    parser.add_argument("--fps", type=int, default=None, help="帧率 (不指定则自动选择)")
    parser.add_argument("--output", "-o", type=str, help="输出 JSON 文件路径")
    parser.add_argument("--yaml", "-y", type=str, help="输出 YAML 文件路径")
    parser.add_argument("--opencv", type=str, help="输出 OpenCV 格式文件路径")
    parser.add_argument("--list", "-l", action="store_true", help="列出支持的分辨率")
    args = parser.parse_args()

    # 列出支持的分辨率
    if args.list:
        ctx = rs.context()
        devices = ctx.query_devices()
        if len(devices) > 0:
            resolutions = get_supported_resolutions(devices[0])
            print("\n📋 支持的分辨率:")
            print("-" * 60)
            for sensor_name, profiles in resolutions.items():
                print(f"\n{sensor_name}:")
                seen = set()
                for p in profiles:
                    key = (p['width'], p['height'], p['fps'])
                    if key not in seen:
                        seen.add(key)
                        print(f"  {p['width']}x{p['height']}@{p['fps']}fps ({p['format']})")
        return

    # 导出参数
    data = export_camera_params(args.width, args.height, args.fps)

    if data is None:
        return

    # 保存文件
    if args.output:
        save_json(data, args.output)

    if args.yaml:
        save_yaml(data, args.yaml)

    if args.opencv:
        save_opencv_format(data, args.opencv)

    # 默认保存到当前目录
    if not (args.output or args.yaml or args.opencv):
        default_path = os.path.join(os.path.dirname(__file__), "camera_params.json")
        save_json(data, default_path)


if __name__ == "__main__":
    main()
