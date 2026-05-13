#!/usr/bin/env python3
"""
机械臂多点移动控制
从配置文件读取位姿点，依次移动到各个位置
"""

import rclpy
from rclpy.node import Node
from roarm_msgs.srv import MoveJointCmd
import yaml
import os
import time


class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        self.cli = self.create_client(MoveJointCmd, '/move_joint_cmd')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待 /move_joint_cmd 服务...')

    def move_to_pose(self, pose: dict) -> bool:
        """
        移动到指定位姿

        Args:
            pose: 包含 x, y, z, roll, pitch, yaw 的字典

        Returns:
            bool: 是否成功
        """
        request = MoveJointCmd.Request()
        request.x = pose.get('x', 0.0)
        request.y = pose.get('y', 0.0)
        request.z = pose.get('z', 0.0)
        request.roll = pose.get('roll', 0.0)
        request.pitch = pose.get('pitch', 0.0)
        request.yaw = pose.get('yaw', 0.0)

        future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()

        if result and result.success:
            self.get_logger().info(f'移动成功: {result.message}')
            return True
        else:
            self.get_logger().error(f'移动失败: {result.message if result else "无响应"}')
            return False

    def navigate_waypoints(self, waypoints: list, delay: float = 2.0) -> dict:
        """
        依次移动到多个位姿点

        Args:
            waypoints: 位姿列表，每个元素为包含 x, y, z 等的字典
            delay: 移动完成后等待时间（秒）

        Returns:
            dict: 包含成功/失败统计
        """
        results = {'success': 0, 'failed': 0, 'total': len(waypoints)}

        for i, pose in enumerate(waypoints):
            self.get_logger().info(
                f'[{i+1}/{len(waypoints)}] 移动到: '
                f'x={pose.get("x", 0):.3f}, y={pose.get("y", 0):.3f}, z={pose.get("z", 0):.3f}'
            )

            success = self.move_to_pose(pose)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1

            if delay > 0 and i < len(waypoints) - 1:
                time.sleep(delay)

        return results


def load_waypoints_config(config_path: str) -> list:
    """
    从 YAML 配置文件加载位姿点

    Args:
        config_path: 配置文件路径

    Returns:
        list: 位姿列表
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('waypoints', [])


def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()

    # 配置文件路径（默认）
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(config_dir, 'waypoints_config.yaml')

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        navigator.get_logger().error(f'配置文件不存在: {config_path}')
        navigator.destroy_node()
        rclpy.shutdown()
        return

    # 加载位姿配置
    waypoints = load_waypoints_config(config_path)
    navigator.get_logger().info(f'加载了 {len(waypoints)} 个位姿点')

    if not waypoints:
        navigator.get_logger().error('配置文件中没有位姿点')
        navigator.destroy_node()
        rclpy.shutdown()
        return

    # 执行移动
    results = navigator.navigate_waypoints(waypoints, delay=2.0)

    # 打印统计结果
    print("\n" + "="*50)
    print("移动完成统计:")
    print("="*50)
    print(f"  总数: {results['total']}")
    print(f"  成功: {results['success']}")
    print(f"  失败: {results['failed']}")
    print("="*50 + "\n")

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()