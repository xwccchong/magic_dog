import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from sensor_msgs.msg import PointCloud2

class CloudSubscriber(Node):
    def __init__(self):
        super().__init__('mid360_cloud_subscriber')

        # ⚠️ 关键修改：将话题名称替换为 Mid360 实际发布的话题
        # 如果你不确定，可以通过 `ros2 topic list` 查找
        # ros2 不需要添加rt前缀
        # topic_name = 'rt/unitree/slam_lidar/points'  # 以前是 '/utlidar/cloud'
        topic_name = 'unitree/slam_lidar/points'

        # 关键：传感器数据通常使用 BEST_EFFORT QoS，必须匹配否则收不到数据
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.subscription = self.create_subscription(
            PointCloud2,
            topic_name,
            self.cloud_callback,
            qos_profile
        )
        self.get_logger().info(f"正在监听点云话题: {topic_name}")

    def cloud_callback(self, msg: PointCloud2):
        # 对应 C++ 代码中的 std::cout 打印逻辑
        self.get_logger().info('Received a raw cloud here!')
        self.get_logger().info(f'\tstamp = {msg.header.stamp.sec}.{msg.header.stamp.nanosec}')
        self.get_logger().info(f'\tframe = {msg.header.frame_id}')
        self.get_logger().info(f'\tpoints number = {msg.width * msg.height}')
        self.get_logger().info('\n')

def main(args=None):
    rclpy.init(args=args)
    node = CloudSubscriber()
    
    try:
        # 对应 C++ 代码中的 while(true) { sleep(10); }，保持节点持续运行监听
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('节点已手动停止')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()