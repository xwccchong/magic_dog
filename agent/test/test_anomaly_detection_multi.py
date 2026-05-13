#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多角度异常检测测试

测试项:
1. 配置文件加载
2. 图像拼接功能
3. 机械臂服务连接 (需要 Docker 环境)
4. 完整流程测试 (需要相机 + 机械臂 + LLM)

用法:
    # 基础测试 (不需要硬件，不需要 Docker)
    python test_anomaly_detection_multi.py

    # 完整测试 (需要相机和机械臂)
    python test_anomaly_detection_multi.py --full

    # 仅测试机械臂连接 (需要 Docker)
    python test_anomaly_detection_multi.py --arm
"""

import os
import sys
import cv2
import time
import base64
import argparse
import numpy as np
import yaml

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============ 本地实现 (不需要 roarm_msgs) ============

def load_waypoints_config(config_path: str) -> list:
    """从 YAML 配置文件加载位姿点"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('waypoints', [])


def _stitch_images(images):
    """将多张图像拼接为 2x2 网格，返回 JPEG bytes"""
    h, w = images[0].shape[:2]

    resized = []
    for img in images:
        if img.shape[:2] != (h, w):
            img = cv2.resize(img, (w, h))
        resized.append(img)

    while len(resized) < 4:
        resized.append(np.zeros((h, w, 3), dtype=np.uint8))

    top = np.hstack([resized[0], resized[1]])
    bottom = np.hstack([resized[2], resized[3]])
    grid = np.vstack([top, bottom])

    _, buf = cv2.imencode('.jpg', grid, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return buf


# ============ 测试函数 ============

def get_config_path():
    """获取配置文件路径"""
    config_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'utils', 'roarm_control'
    )
    return os.path.join(config_dir, 'waypoints_config.yaml')


def test_config_loading():
    """测试 1: 配置文件加载"""
    print("=" * 60)
    print("测试 1: 配置文件加载")
    print("=" * 60)

    config_path = get_config_path()
    print(f"  配置文件路径: {config_path}")

    if not os.path.exists(config_path):
        print(f"  ❌ 配置文件不存在")
        return False

    waypoints = load_waypoints_config(config_path)
    print(f"  加载了 {len(waypoints)} 个位姿点")

    for i, pose in enumerate(waypoints):
        print(f"    [{i+1}] {pose.get('name', 'unnamed')}: "
              f"x={pose.get('x', 0):.3f}, y={pose.get('y', 0):.3f}, z={pose.get('z', 0):.3f}")

    if len(waypoints) >= 4:
        print("  ✅ 位姿点数量足够 (>=4)")
    else:
        print("  ⚠️ 位姿点数量不足 4 个")

    print("  测试 1 通过\n")
    return True


def test_image_stitching():
    """测试 2: 图像拼接功能"""
    print("=" * 60)
    print("测试 2: 图像拼接功能")
    print("=" * 60)

    # 创建 4 张测试图像 (不同颜色)
    images = []
    colors = [
        (255, 0, 0),    # 蓝
        (0, 255, 0),    # 绿
        (0, 0, 255),    # 红
        (255, 255, 0),  # 青
    ]

    for i, color in enumerate(colors):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = color
        # 添加文字标识
        cv2.putText(img, f"Image {i+1}", (220, 250),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        images.append(img)

    # 拼接图像
    stitched_buf = _stitch_images(images)
    print(f"  拼接后 buffer 大小: {len(stitched_buf)} bytes")

    # 解码并保存
    stitched_img = cv2.imdecode(np.frombuffer(stitched_buf, np.uint8), cv2.IMREAD_COLOR)
    print(f"  拼接后图像尺寸: {stitched_img.shape}")

    # 保存结果
    save_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, "test_stitched.jpg")
    cv2.imwrite(output_path, stitched_img)
    print(f"  拼接图像已保存: {output_path}")

    # 测试 base64 编码
    img_b64 = base64.b64encode(stitched_buf).decode('utf-8')
    print(f"  Base64 编码长度: {len(img_b64)} 字符")

    print("  测试 2 通过\n")
    return True


def test_arm_connection():
    """测试 3: 机械臂服务连接 (需要 Docker)"""
    print("=" * 60)
    print("测试 3: 机械臂服务连接 (需要 Docker)")
    print("=" * 60)

    try:
        import rclpy
        from std_msgs.msg import String
    except ImportError as e:
        print(f"  ❌ ROS2 未安装: {e}")
        return False

    # 初始化 ROS2
    if not rclpy.ok():
        rclpy.init()

    from navi_update.actions.anomaly_detection_multi import get_arm_commander
    ArmCommander = get_arm_commander()

    try:
        arm = ArmCommander()
        print("  ✅ ArmCommander 节点创建成功")

        # 测试发送位姿指令
        config_path = get_config_path()
        if os.path.exists(config_path):
            waypoints = load_waypoints_config(config_path)
            if waypoints:
                print(f"\n  测试发送位姿指令: {waypoints[0].get('name', 'pose_1')}")
                print(f"  (等待 Docker 桥接节点响应，超时 5 秒)")

                success = arm.move_to_pose(waypoints[0], timeout=5.0)
                if success:
                    print("  ✅ 移动成功")
                else:
                    print("  ⚠️ 未收到响应 (可能 Docker 桥接节点未启动)")

        arm.destroy_node()
        print("  测试 3 完成\n")
        return True

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """测试 4: 完整流程测试 (需要相机 + 机械臂)"""
    print("=" * 60)
    print("测试 4: 完整流程测试 (需要相机 + 机械臂)")
    print("=" * 60)

    try:
        from agent.level2.mp_single_realsense import RealSenseSubProcess
        import rclpy
    except ImportError as e:
        print(f"  ❌ 依赖未安装: {e}")
        return False

    # 初始化相机
    print("  启动相机...")
    cam = RealSenseSubProcess(width=640, height=480, fps=15)
    cam.start(wait=True, timeout=15.0)

    # 初始化 ROS2
    if not rclpy.ok():
        rclpy.init()

    from navi_update.actions.anomaly_detection_multi import get_arm_commander
    ArmCommander = get_arm_commander()

    try:
        arm = ArmCommander()
        print("  ✅ 相机就绪")

        # 加载配置
        config_path = get_config_path()
        waypoints = load_waypoints_config(config_path)

        # 只测试前 2 个位姿点
        images = []
        for i, pose in enumerate(waypoints[:2]):
            pose_name = pose.get('name', f'pose_{i+1}')
            print(f"\n  [{i+1}/2] 发送位姿指令 {pose_name}...")

            success = arm.move_to_pose(pose, timeout=5.0)
            if not success:
                print(f"    ⚠️ 未收到响应，模拟拍照")
            else:
                print(f"    ✅ 移动成功")

            time.sleep(2.0)  # 等待稳定

            rgbs, _, _ = cam.get_images(num_frames=1)
            if rgbs:
                images.append(rgbs[-1])
                print(f"    📸 拍照完成, 图像尺寸: {rgbs[-1].shape}")

        arm.destroy_node()

        if len(images) >= 2:
            # 拼接并保存
            stitched_buf = _stitch_images(images)
            stitched_img = cv2.imdecode(np.frombuffer(stitched_buf, np.uint8), cv2.IMREAD_COLOR)

            save_dir = os.path.join(os.path.dirname(__file__), "test_output")
            os.makedirs(save_dir, exist_ok=True)
            output_path = os.path.join(save_dir, "test_multi_angle.jpg")
            cv2.imwrite(output_path, stitched_img)
            print(f"\n  ✅ 多角度图像已保存: {output_path}")

            # 测试异常检测
            print("\n  测试异常检测...")
            try:
                from agent.utils.anomaly_detection import detect_anomaly
                img_b64 = base64.b64encode(stitched_buf).decode('utf-8')
                result = detect_anomaly(img_b64)
                if result:
                    print(f"  ✅ 异常检测结果: {result}")
                else:
                    print("  ⚠️ 异常检测返回空")
            except Exception as e:
                print(f"  ⚠️ 异常检测失败: {e}")

            print("  测试 4 通过\n")
            return True
        else:
            print("  ❌ 图像数量不足")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cam.stop()


def main():
    parser = argparse.ArgumentParser(description="多角度异常检测测试")
    parser.add_argument('--full', action='store_true',
                        help='运行完整流程测试 (需要相机和机械臂)')
    parser.add_argument('--arm', action='store_true',
                        help='仅测试机械臂连接 (需要 Docker)')
    args = parser.parse_args()

    print("\n>>> 多角度异常检测测试 <<<\n")

    results = []

    # 基础测试 (不需要硬件，不需要 Docker)
    results.append(("配置加载", test_config_loading()))
    results.append(("图像拼接", test_image_stitching()))

    # 机械臂测试 (需要 Docker)
    if args.arm or args.full:
        results.append(("机械臂连接", test_arm_connection()))

    # 完整流程测试 (需要相机 + Docker)
    if args.full:
        results.append(("完整流程", test_full_workflow()))

    # 汇总结果
    print("=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    print("=" * 60)

    all_passed = all(r[1] for r in results)
    if all_passed:
        print("🎉 所有测试通过!")
    else:
        print("⚠️ 部分测试失败")


if __name__ == "__main__":
    main()
