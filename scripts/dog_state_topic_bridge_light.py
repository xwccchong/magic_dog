#!/usr/bin/env python3
import argparse
import math
import multiprocessing as mp
import os
import queue
import signal
import sys
import threading
import time


def normalize_quaternion(w, x, y, z):
    norm = math.sqrt(w * w + x * x + y * y + z * z)
    if norm <= 1e-9:
        return 1.0, 0.0, 0.0, 0.0
    return w / norm, x / norm, y / norm, z / norm


def compute_publish_period(publish_rate):
    if publish_rate is None or publish_rate <= 0.0:
        return None
    return 1.0 / max(publish_rate, 1.0)


def make_qos_profile(reliability, depth):
    from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy

    reliability_policy = {
        "best_effort": ReliabilityPolicy.BEST_EFFORT,
        "reliable": ReliabilityPolicy.RELIABLE,
    }[reliability]

    return QoSProfile(
        reliability=reliability_policy,
        history=HistoryPolicy.KEEP_LAST,
        depth=depth,
        durability=DurabilityPolicy.VOLATILE,
    )


def dds_reader_worker(data_queue, network_interface, state_topic, publish_rate):
    os.environ.pop("CYCLONEDDS_URI", None)
    os.environ.setdefault("CYCLONEDDS_HOME", os.path.expanduser("~/cyclonedds_ws/install/cyclonedds"))
    os.environ["LD_LIBRARY_PATH"] = (
        os.path.join(os.environ["CYCLONEDDS_HOME"], "lib")
        + ":"
        + os.environ.get("LD_LIBRARY_PATH", "")
    )
    sys.path.insert(0, "/home/unitree/unitree_sdk2_python")

    from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_

    publish_period = compute_publish_period(publish_rate)
    next_publish_time = 0.0

    def handle_state(msg):
        nonlocal next_publish_time
        if publish_period is not None:
            now = time.monotonic()
            if now < next_publish_time:
                return
            next_publish_time = now + publish_period

        imu_state = msg.imu_state
        payload = {
            "stamp_sec": int(msg.stamp.sec) if msg.stamp else 0,
            "stamp_nanosec": int(msg.stamp.nanosec) if msg.stamp else 0,
            "position": [float(msg.position[i]) for i in range(3)],
            "velocity": [float(msg.velocity[i]) for i in range(3)],
            "body_height": float(msg.body_height),
            "yaw_speed": float(msg.yaw_speed),
            "quaternion": [float(imu_state.quaternion[i]) for i in range(4)],
            "gyroscope": [float(imu_state.gyroscope[i]) for i in range(3)],
            "accelerometer": [float(imu_state.accelerometer[i]) for i in range(3)],
        }
        while True:
            try:
                data_queue.put_nowait(payload)
                break
            except queue.Full:
                try:
                    data_queue.get_nowait()
                except queue.Empty:
                    break
            except queue.Empty:
                break

    print(f"[dds_reader] init iface={network_interface} topic={state_topic}", flush=True)
    ChannelFactoryInitialize(0, network_interface)
    sub = ChannelSubscriber(state_topic, SportModeState_)
    sub.Init(handle_state, 10)
    print("[dds_reader] subscriber ready", flush=True)
    while True:
        time.sleep(1.0)


def ros_publisher_worker(data_queue, args):
    import rclpy
    from nav_msgs.msg import Odometry
    from rclpy.node import Node
    from sensor_msgs.msg import Imu

    class DogStatePublisher(Node):
        def __init__(self):
            super().__init__("dog_state_topic_bridge")
            odom_qos = make_qos_profile(args.odom_qos, args.odom_qos_depth)
            self.odom_pub = self.create_publisher(Odometry, args.odom_topic, odom_qos)
            self.imu_pub = None
            if args.publish_imu:
                self.imu_pub = self.create_publisher(Imu, args.imu_topic, 10)
            self.message_count = 0
            self.stop_event = threading.Event()
            self.queue_thread = None
            timer_period = compute_publish_period(args.publish_rate)
            if timer_period is not None:
                self.create_timer(timer_period, self.drain_queue)
            else:
                # Unlimited mode publishes each source sample as it arrives.
                self.queue_thread = threading.Thread(target=self.forward_queue, daemon=True)
                self.queue_thread.start()
            imu_status = args.imu_topic if args.publish_imu else "disabled"
            rate_status = f"{args.publish_rate:.1f} Hz" if timer_period is not None else "source-rate"
            self.get_logger().info(
                f"ROS publisher ready: odom={args.odom_topic}, imu={imu_status}, "
                f"rate={rate_status}, odom_qos={args.odom_qos}, "
                f"odom_qos_depth={args.odom_qos_depth}"
            )

        def stop(self):
            self.stop_event.set()
            if self.queue_thread is not None:
                self.queue_thread.join(timeout=1.0)

        def stamp_from_payload(self, payload):
            stamp = self.get_clock().now().to_msg()
            if payload["stamp_sec"] != 0 or payload["stamp_nanosec"] != 0:
                stamp.sec = payload["stamp_sec"]
                stamp.nanosec = payload["stamp_nanosec"]
            return stamp

        def forward_queue(self):
            while not self.stop_event.is_set():
                try:
                    payload = data_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                self.publish_payload(payload)

        def drain_queue(self):
            latest = None
            while True:
                try:
                    latest = data_queue.get_nowait()
                except queue.Empty:
                    break
            if latest is not None:
                self.publish_payload(latest)

        def publish_payload(self, payload):
            stamp = self.stamp_from_payload(payload)
            qw, qx, qy, qz = normalize_quaternion(*payload["quaternion"])

            odom = Odometry()
            odom.header.stamp = stamp
            odom.header.frame_id = args.odom_frame
            odom.child_frame_id = args.base_frame
            odom.pose.pose.position.x = payload["position"][0]
            odom.pose.pose.position.y = payload["position"][1]
            odom.pose.pose.position.z = payload["body_height"] if args.use_body_height_as_z else 0.0
            odom.pose.pose.orientation.w = qw
            odom.pose.pose.orientation.x = qx
            odom.pose.pose.orientation.y = qy
            odom.pose.pose.orientation.z = qz
            odom.twist.twist.linear.x = payload["velocity"][0]
            odom.twist.twist.linear.y = payload["velocity"][1]
            odom.twist.twist.linear.z = payload["velocity"][2]
            odom.twist.twist.angular.z = payload["yaw_speed"]
            odom.pose.covariance[0] = 0.05
            odom.pose.covariance[7] = 0.05
            odom.pose.covariance[35] = 0.10
            odom.twist.covariance[0] = 0.05
            odom.twist.covariance[7] = 0.05
            odom.twist.covariance[35] = 0.10
            self.odom_pub.publish(odom)

            if self.imu_pub is not None:
                imu = Imu()
                imu.header.stamp = stamp
                imu.header.frame_id = args.base_frame
                imu.orientation.w = qw
                imu.orientation.x = qx
                imu.orientation.y = qy
                imu.orientation.z = qz
                imu.angular_velocity.x = payload["gyroscope"][0]
                imu.angular_velocity.y = payload["gyroscope"][1]
                imu.angular_velocity.z = payload["gyroscope"][2]
                imu.linear_acceleration.x = payload["accelerometer"][0]
                imu.linear_acceleration.y = payload["accelerometer"][1]
                imu.linear_acceleration.z = payload["accelerometer"][2]
                imu.orientation_covariance[0] = -1.0
                imu.angular_velocity_covariance[0] = -1.0
                imu.linear_acceleration_covariance[0] = -1.0
                self.imu_pub.publish(imu)

            self.message_count += 1
            if self.message_count == 1 or self.message_count % 200 == 0:
                self.get_logger().info(
                    f"published {self.message_count} dog state samples "
                    f"(x={odom.pose.pose.position.x:.3f}, y={odom.pose.pose.position.y:.3f})"
                )

    rclpy.init(args=None)
    node = DogStatePublisher()
    try:
        rclpy.spin(node)
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--network-interface", default="eth0")
    parser.add_argument("--state-topic", default="rt/sportmodestate")
    parser.add_argument("--odom-topic", default="/dog_odom")
    parser.add_argument("--imu-topic", default="/dog_imu_raw")
    parser.add_argument("--publish-rate", type=float, default=50.0)
    parser.add_argument("--publish-imu", action="store_true")
    parser.add_argument("--odom-frame", default="odom")
    parser.add_argument("--base-frame", default="base_link")
    parser.add_argument("--use-body-height-as-z", action="store_true")
    parser.add_argument("--odom-qos", choices=("reliable", "best_effort"), default="reliable")
    parser.add_argument("--odom-qos-depth", type=int, default=10)
    return parser.parse_args()


def main():
    args = parse_args()
    mp.set_start_method("spawn", force=True)
    data_queue = mp.Queue(maxsize=1)

    dds_proc = mp.Process(
        target=dds_reader_worker,
        args=(data_queue, args.network_interface, args.state_topic, args.publish_rate),
        daemon=True,
    )
    ros_proc = mp.Process(target=ros_publisher_worker, args=(data_queue, args), daemon=True)

    dds_proc.start()
    ros_proc.start()

    def stop_children(_signum, _frame):
        dds_proc.terminate()
        ros_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_children)
    signal.signal(signal.SIGTERM, stop_children)

    while True:
        if not dds_proc.is_alive():
            ros_proc.terminate()
            raise RuntimeError("DDS reader process exited")
        if not ros_proc.is_alive():
            dds_proc.terminate()
            raise RuntimeError("ROS publisher process exited")
        time.sleep(1.0)


if __name__ == "__main__":
    main()
