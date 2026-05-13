#!/usr/bin/env python3
"""
实时订阅 /slam_info 话题，提取并显示 currentPose 的 7 个参数
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import sys

class PoseExtractor(Node):
    def __init__(self):
        super().__init__('pose_extractor')
        self.subscription = self.create_subscription(
            String,
            '/slam_info',
            self.listener_callback,
            10
        )
        self.current_pose = None
        self.pose_received = False
        
    def listener_callback(self, msg):
        try:
            data = json.loads(msg.data)
            
            if 'data' in data and 'currentPose' in data['data']:
                pose = data['data']['currentPose']
                
                # 检查位姿是否有效（非全零）
                if pose.get('x', 0) != 0 or pose.get('y', 0) != 0:
                    self.current_pose = {
                        'x': pose.get('x', 0.0),
                        'y': pose.get('y', 0.0),
                        'z': pose.get('z', 0.0),
                        'qx': pose.get('q_x', 0.0),
                        'qy': pose.get('q_y', 0.0),
                        'qz': pose.get('q_z', 0.0),
                        'qw': pose.get('q_w', 1.0)
                    }
                    self.pose_received = True
                    
        except json.JSONDecodeError as e:
            self.get_logger().error(f'JSON decode error: {e}')
        except Exception as e:
            self.get_logger().error(f'Error in callback: {e}')


def get_current_pose_once(timeout=2.0):
    """
    获取一次当前位姿
    
    Args:
        timeout: 超时时间（秒）
        
    Returns:
        dict: 包含 x, y, z, qx, qy, qz, qw 的字典，失败返回 None
    """
    # 初始化 ROS2（如果尚未初始化）
    if not rclpy.ok():
        rclpy.init()
    
    node = PoseExtractor()
    
    # 自旋等待数据
    start_time = node.get_clock().now()
    timeout_duration = rclpy.duration.Duration(seconds=timeout)
    
    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)
        
        if node.pose_received:
            result = node.current_pose
            node.destroy_node()
            return result
        
        # 检查超时
        if (node.get_clock().now() - start_time) > timeout_duration:
            print(f"⚠️ 获取位姿超时（{timeout}秒）")
            node.destroy_node()
            return None
    
    node.destroy_node()
    return None


def main(args=None):
    """命令行模式"""
    rclpy.init(args=args)
    
    node = PoseExtractor()
    
    # 检查是否使用简单模式
    simple_mode = len(sys.argv) > 1 and sys.argv[1] == 'simple'
    
    if simple_mode:
        print("# x y z q_x q_y q_z q_w")
    else:
        print("📡 开始订阅 /slam_info 话题...")
        print("等待位姿数据...\n")
    
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            
            if node.pose_received:
                pose = node.current_pose
                
                if simple_mode:
                    # 简单模式：只输出数值
                    print(f"{pose['x']:.6f} {pose['y']:.6f} {pose['z']:.6f} "
                          f"{pose['qx']:.6f} {pose['qy']:.6f} {pose['qz']:.6f} {pose['qw']:.6f}")
                    # 👇 新增：获取一次数据后立即跳出循环，结束程序
                    break
                else:
                    # 详细模式
                    print(f"📍 当前位姿:")
        # while rclpy.ok():
        #     rclpy.spin_once(node, timeout_sec=0.1)
            
        #     if node.pose_received:
        #         pose = node.current_pose
                
        #         if simple_mode:
        #             # 简单模式：只输出数值
        #             print(f"{pose['x']:.6f} {pose['y']:.6f} {pose['z']:.6f} "
        #                   f"{pose['qx']:.6f} {pose['qy']:.6f} {pose['qz']:.6f} {pose['qw']:.6f}")
        #         else:
        #             # 详细模式
        #             print(f"📍 当前位姿:")
        #             print(f"   Position: x={pose['x']:.6f}, y={pose['y']:.6f}, z={pose['z']:.6f}")
        #             print(f"   Orientation: qx={pose['qx']:.6f}, qy={pose['qy']:.6f}, "
        #                   f"qz={pose['qz']:.6f}, qw={pose['qw']:.6f}")
        #             print()
                
                node.pose_received = False  # 重置标志
                
    except KeyboardInterrupt:
        print("\n⏹️  已停止")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()