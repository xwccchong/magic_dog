#!/usr/bin/env python3
import os
import sys
import time
import json
import struct

# 设置环境变量
os.environ["CYCLONEDDS_URI"] = '<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="eth0" priority="default" multicast="default" /></Interfaces></General></Domain></CycloneDDS>'
os.environ["RMW_IMPLEMENTATION"] = "rmw_cyclonedds_cpp"

# 添加 ROS2 Python 路径
sys.path.insert(0, "/opt/ros/foxy/lib/python3.8/site-packages")

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from unitree_go.msg import Go2FrontVideoData

resolution = sys.argv[1] if len(sys.argv) > 1 else "720p"
resolution_map = {
    "720p": "video720p",
    "360p": "video360p",
    "180p": "video180p",
}
data_attr = resolution_map.get(resolution, "video720p")

rclpy.init()
node = rclpy.create_node('front_camera_subscriber')

def callback(msg):
    data = getattr(msg, data_attr)
    if len(data) > 0:
        # 输出格式: [4字节长度][数据]
        packed = struct.pack('<I', len(data)) + bytes(data)
        sys.stdout.buffer.write(packed)
        sys.stdout.buffer.flush()

qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)

sub = node.create_subscription(Go2FrontVideoData, '/frontvideostream', callback, qos)

try:
    while True:
        rclpy.spin_once(node, timeout_sec=0.1)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.shutdown()
