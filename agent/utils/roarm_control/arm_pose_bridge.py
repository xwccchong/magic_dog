#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂位姿指令桥接节点 (运行在 Docker 中)

功能:
1. 订阅 /arm_pose_command 话题 (接收宿主机指令)
2. 调用 /move_joint_cmd 服务 (控制机械臂)
3. 发布 /arm_pose_result 话题 (返回执行结果)

用法:
    # 在 Docker 容器中运行
    source /opt/ros/humble/setup.bash
    source /workspace/roarm_ws/roarm_ws/install/setup.bash
    python3 arm_pose_bridge.py
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
from roarm_msgs.srv import MoveJointCmd
import json
import threading


class ArmPoseBridge(Node):
    def __init__(self):
        super().__init__('arm_pose_bridge')

        # 使用 ReentrantCallbackGroup 允许并发执行
        self.callback_group = ReentrantCallbackGroup()

        # 订阅位姿指令话题
        self.subscription = self.create_subscription(
            String,
            '/arm_pose_command',
            self.pose_command_callback,
            10,
            callback_group=self.callback_group
        )

        # 发布执行结果话题
        self.result_publisher = self.create_publisher(String, '/arm_pose_result', 10)

        # 创建机械臂服务客户端
        self.cli = self.create_client(
            MoveJointCmd,
            '/move_joint_cmd',
            callback_group=self.callback_group
        )

        # 等待服务可用
        self.get_logger().info('等待 /move_joint_cmd 服务...')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            pass
        self.get_logger().info('✅ /move_joint_cmd 服务已连接')

        self.get_logger().info('🚀 Arm Pose Bridge 已启动，等待指令...')

    def pose_command_callback(self, msg):
        """处理位姿指令"""
        try:
            # 解析 JSON 指令
            pose = json.loads(msg.data)
            self.get_logger().info(f'📥 收到指令: {pose}')

            # 调用机械臂服务
            request = MoveJointCmd.Request()
            request.x = float(pose.get('x', 0.0))
            request.y = float(pose.get('y', 0.0))
            request.z = float(pose.get('z', 0.0))
            request.roll = float(pose.get('roll', 0.0))
            request.pitch = float(pose.get('pitch', 0.0))
            request.yaw = float(pose.get('yaw', 0.0))

            # 异步调用服务
            future = self.cli.call_async(request)

            # 等待服务完成 (使用回调方式，避免阻塞)
            def service_done_callback(future):
                result = future.result()
                self._publish_result(result, pose)

            future.add_done_callback(service_done_callback)

        except json.JSONDecodeError as e:
            self.get_logger().error(f'JSON 解析失败: {e}')
        except Exception as e:
            self.get_logger().error(f'处理指令失败: {e}')

    def _publish_result(self, result, pose):
        """发布执行结果"""
        result_msg = String()
        if result and result.success:
            result_msg.data = json.dumps({
                'success': True,
                'message': result.message,
                'pose': pose
            })
            self.get_logger().info(f'✅ 移动成功: {result.message}')
        else:
            result_msg.data = json.dumps({
                'success': False,
                'message': result.message if result else '服务无响应',
                'pose': pose
            })
            self.get_logger().error(f'❌ 移动失败: {result.message if result else "无响应"}')

        # 发布结果
        self.result_publisher.publish(result_msg)
        self.get_logger().info(f'📤 结果已发布: success={result.success if result else False}')


def main(args=None):
    rclpy.init(args=args)
    bridge = ArmPoseBridge()

    # 使用多线程执行器，支持并发回调
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(bridge)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        bridge.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()