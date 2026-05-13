# -*- coding: utf-8 -*-
"""
多角度异常检测动作：
机械臂移动到多个位置（4个角度），每个位置拍照，
拼接为一张图后发送服务端 + LLM 视觉分析

架构:
  宿主机 → 发布 /arm_pose_command (JSON) → Docker arm_pose_bridge → /move_joint_cmd 服务
  Docker arm_pose_bridge → 发布 /arm_pose_result (JSON) → 宿主机订阅
"""

import os
import json
import time
import cv2
import base64
import numpy as np
import yaml
import subprocess

# 设置 ROS2 环境变量（必须在导入 rclpy 之前）
def _setup_ros2_env():
    """设置 ROS2 环境变量"""
    # 获取 ROS2 foxy 的环境变量
    result = subprocess.run(
        ['bash', '-c', 'source /opt/ros/foxy/setup.bash && env'],
        capture_output=True,
        text=True
    )

    for line in result.stdout.splitlines():
        if '=' in line:
            key, _, value = line.partition('=')
            # 只设置 ROS2 相关的环境变量
            if any(x in key for x in ['ROS', 'AMENT', 'CYCLONE', 'COLCON', 'PYTHONPATH']):
                os.environ[key] = value

    # 设置 ROS_DOMAIN_ID=99 用于与 Docker 中的机械臂桥接节点通信
    # 注意：机器狗本体通信需要 ROS_DOMAIN_ID=0
    os.environ['ROS_DOMAIN_ID'] = '99'

from agent.utils.anomaly_detection import detect_anomaly


def _get_arm_commander_class():
    """延迟导入并返回 ArmCommander 类"""
    # 先设置 ROS2 环境（必须在导入 rclpy 之前）
    _setup_ros2_env()

    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String

    class ArmCommander(Node):
        """宿主机机械臂指令节点，通过话题与 Docker 桥接节点通信"""

        def __init__(self):
            super().__init__('host_arm_commander')

            # 发布位姿指令
            self.command_pub = self.create_publisher(String, '/arm_pose_command', 10)

            # 订阅执行结果
            self._result = None
            self._result_received = False
            self.result_sub = self.create_subscription(
                String, '/arm_pose_result', self._result_callback, 10
            )

            self.get_logger().info('等待 Docker 桥接节点连接...')

        def _result_callback(self, msg):
            """接收 Docker 桥接节点返回的执行结果"""
            try:
                self._result = json.loads(msg.data)
                self._result_received = True
                self.get_logger().info(f'收到结果: {self._result}')
            except json.JSONDecodeError:
                self.get_logger().error(f'结果解析失败: {msg.data}')

        def move_to_pose(self, pose: dict, timeout: float = 10.0) -> bool:
            """
            发送位姿指令并等待结果

            Args:
                pose: 包含 x, y, z, roll, pitch 的字典
                timeout: 等待结果超时时间 (秒)

            Returns:
                bool: 是否成功 (超时则返回 False)
            """
            self._result = None
            self._result_received = False

            # 等待订阅者连接 (Docker 桥接节点)
            wait_time = 0.0
            while self.command_pub.get_subscription_count() == 0 and wait_time < 3.0:
                rclpy.spin_once(self, timeout_sec=0.1)
                wait_time += 0.1

            sub_count = self.command_pub.get_subscription_count()
            if sub_count == 0:
                self.get_logger().warn('没有订阅者连接，可能 Docker 桥接节点未启动')

            # 发送位姿指令
            cmd_msg = String()
            cmd_msg.data = json.dumps(pose)
            self.command_pub.publish(cmd_msg)
            self.get_logger().info(f'发送指令: {pose}')

            # 等待结果
            start_time = time.time()
            while not self._result_received and (time.time() - start_time) < timeout:
                rclpy.spin_once(self, timeout_sec=0.1)

            if not self._result_received:
                self.get_logger().warn(f'等待结果超时 ({timeout}s)，可能 Docker 桥接节点未启动')
                return False

            return self._result.get('success', False)

    return ArmCommander


# 模块级别导出 ArmCommander（延迟加载）
# 用法: from anomaly_detection_multi import get_arm_commander
#       ArmCommander = get_arm_commander()
def get_arm_commander():
    """获取 ArmCommander 类（延迟加载，兼容外部导入）"""
    return _get_arm_commander_class()


def load_waypoints_config(config_path: str) -> list:
    """从 YAML 配置文件加载位姿点"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('waypoints', [])


def _stitch_images_panorama(images):
    """
    使用 OpenCV Stitcher 将多张具有重叠视角的图像进行全景融合拼接。
    如果特征点匹配失败（例如图像之间没有重叠区域），则自动回退到 2x2 网格拼接。
    返回 JPEG bytes。
    """
    if not images or len(images) == 0:
        return None
        
    if len(images) == 1:
        _, buf = cv2.imencode('.jpg', images[0], [cv2.IMWRITE_JPEG_QUALITY, 85])
        return buf

    # 1. 创建全景拼接器
    # cv2.Stitcher_PANORAMA 适合标准的透视相机旋转拍摄
    # cv2.Stitcher_SCANS 适合平行移动相机拍摄的情况（根据你的实际情况切换）
    stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
    
    # 2. 执行自动特征匹配与拼接
    # status 状态码: 0=OK, 1=需要更多图像, 2=图像分辨率不匹配, 3=相机参数不匹配
    status, pano = stitcher.stitch(images)
    
    # 3. 检查结果并输出
    if status == cv2.Stitcher_OK:
        print("✅ 全景图像特征匹配与融合成功！")
        # 拼接成功，压缩为 JPEG 字节流
        _, buf = cv2.imencode('.jpg', pano, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return buf
    else:
        # ⚠️ 关键保底机制：
        # 如果相机拍摄的四个角度完全没有重叠部分（盲区太大），算法无法找到相同特征点，就会拼接失败。
        print(f"⚠️ 全景拼接失败 (OpenCV 状态码: {status})。特征点不足或无重叠区域，已回退到基础网格拼接。")
        
        # 调用你原来的网格拼接函数作为备选方案
        return _stitch_images(images)

def _stitch_images(images, border_thickness=15, border_color=(0, 0, 255)):
    """
    将多张图像拼接为 2x2 网格，并在中间添加红色的十字分割线。
    
    :param images: 图像列表
    :param border_thickness: 分割线的宽度（像素）
    :param border_color: 分割线颜色，默认 (0, 0, 255) 是 OpenCV 中的红色
    """
    if not images or len(images) == 0:
        return None
        
    h, w = images[0].shape[:2]

    # 1. 统一尺寸与补齐空位
    resized = []
    for img in images:
        if img.shape[:2] != (h, w):
            img = cv2.resize(img, (w, h))
        resized.append(img)

    while len(resized) < 4:
        resized.append(np.zeros((h, w, 3), dtype=np.uint8))

    # 2. 制作垂直红色隔离带
    v_sep = np.full((h, border_thickness, 3), border_color, dtype=np.uint8)
    
    # 3. 水平拼接（左图 + 红色隔离带 + 右图）
    top = np.hstack([resized[0], v_sep, resized[1]])
    bottom = np.hstack([resized[2], v_sep, resized[3]])

    # 4. 制作水平红色隔离带
    total_w = top.shape[1] 
    h_sep = np.full((border_thickness, total_w, 3), border_color, dtype=np.uint8)

    # 5. 垂直拼接（上排 + 红色隔离带 + 下排）
    grid = np.vstack([top, h_sep, bottom])

    # 6. 编码输出 JPEG
    _, buf = cv2.imencode('.jpg', grid, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return buf


async def execute(cam, websocket, data, inspection_results):
    """
    多角度异常检测：
    1. 机械臂移动到 4 个位置，每个位置拍照
    2. 拼接为一张图，通过 websocket 发送 server
    3. 调用 LLM 异常检测 + 回复初始位姿
    """
    location = data.get("location", "未指定")
    print(f"🔍 多角度异常检测 ({location}): 启动...")

    # 加载 waypoints
    config_path = "/home/unitree/unitree_sdk2_python/agent/config/waypoints_config.yaml"

    if not os.path.exists(config_path):
        print("⚠️ 机械臂配置文件不存在，跳过多角度检测")
        return

    waypoints = load_waypoints_config(config_path)

    if len(waypoints) < 4:
        print(f"⚠️ 配置的位姿点不足 4 个({len(waypoints)}个)，跳过")
        return

    # 延迟导入 ROS2 相关模块（先设置环境）
    _setup_ros2_env()
    import rclpy

    # 初始化 ROS2
    if not rclpy.ok():
        rclpy.init()

    # 获取 ArmCommander 类（延迟加载）
    ArmCommander = _get_arm_commander_class()
    arm_commander = ArmCommander()

    # 逐点移动 + 拍照
    images = []
    move_delay = 2.0

    for i, pose in enumerate(waypoints[:4]):
        pose_name = pose.get('name', f'pose_{i+1}')

        # 发送位姿指令给 Docker 桥接节点
        success = arm_commander.move_to_pose(pose)

        if not success:
            print(f"   ⚠️ {pose_name} 移动失败 (可能桥接节点未启动)，跳过")
            continue

        # 等待相机稳定
        time.sleep(move_delay)

        rgbs, _, _ = cam.get_images(num_frames=1)
        if rgbs:
            images.append(rgbs[-1])
            print(f"   📸 {pose_name} 拍照完成")
        else:
            print(f"   ⚠️ {pose_name} 相机无数据")

    # 拍照完成后，子线程移动机械臂回到初始位置（不阻塞后续图像处理和异常检测）
    initial_pose = {"x": 0.1, "y": 0.0, "z": 0.1, "roll": 0.0, "pitch": 0.3, "yaw": 0.0}

    def _move_arm_to_initial():
        """子线程：机械臂回到初始位置"""
        try:
            print("   🦾 机械臂正在回到初始位置...")
            arm_commander.move_to_pose(initial_pose, timeout=10.0)
            print("   ✅ 机械臂已回到初始位置")
        except Exception as e:
            print(f"   ⚠️ 机械臂回初始位置失败: {e}")
        finally:
            arm_commander.destroy_node()

    import threading
    return_thread = threading.Thread(target=_move_arm_to_initial, daemon=True)
    return_thread.start()

    if len(images) < 4:
        print(f"⚠️ 只拍到 {len(images)} 张图像，跳过拼接")
        return_thread.join()  # 等待机械臂归位
        return

    # 拼接图像
    print("   🧩 正在拼接多角度图像...")
    stitched_buf = _stitch_images(images)
    # stitched_buf = _stitch_images_panorama(images)
    img_b64 = base64.b64encode(stitched_buf).decode('utf-8')

    # 通过 websocket 发送
    if websocket:
        await websocket.send(json.dumps({
            "type": "photo",
            "data": img_b64,
            "timestamp": time.time()
        }))
        print("   ✓ 多角度拼接图像已发送至服务端")
    else:
        print("   ⚠️ WebSocket 未连接，无法发送图像")

    # LLM 异常检测
    print("   🔍 正在进行异常检测分析...")
    result = detect_anomaly(img_b64)
    if result:
        result["location"] = location
        inspection_results.append(result)
        print(f"   📝 巡检结果已记录 (第{len(inspection_results)}个点)")
    else:
        print("   ⚠️ 异常检测失败，跳过")

    # 等待机械臂归位完成
    return_thread.join()