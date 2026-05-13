#!/usr/bin/env python3
"""
获取当前机械臂末端位姿
调用 /get_pose_cmd 服务并打印结果
"""

import rclpy
from rclpy.node import Node
from roarm_msgs.srv import GetPoseCmd


class PoseGetter(Node):
    def __init__(self):
        super().__init__('pose_getter')
        self.cli = self.create_client(GetPoseCmd, '/get_pose_cmd')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待 /get_pose_cmd 服务...')

    def get_current_pose(self):
        request = GetPoseCmd.Request()
        future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def main(args=None):
    rclpy.init(args=args)
    pose_getter = PoseGetter()

    result = pose_getter.get_current_pose()

    if result:
        print("\n" + "="*50)
        print("当前末端位姿:")
        print("="*50)
        print(f"  位置 (Position):")
        print(f"    x: {result.x:.4f} m")
        print(f"    y: {result.y:.4f} m")
        print(f"    z: {result.z:.4f} m")
        print(f"  姿态 (Orientation):")
        print(f"    roll:  {result.roll:.4f} rad")
        print(f"    pitch: {result.pitch:.4f} rad")
        print(f"    yaw:   {result.yaw:.4f} rad")
        print("="*50 + "\n")
    else:
        pose_getter.get_logger().error('获取位姿失败')

    pose_getter.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()