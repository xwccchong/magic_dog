#!/usr/bin/env bash

set -Eeuo pipefail

WORKSPACE="/home/nvidia/ws_mid360"
ROS_SETUP="/opt/ros/humble/setup.bash"
WS_SETUP="${WORKSPACE}/install/setup.bash"

# ROS 2 Humble 使用系统 Python，避免 Conda 环境污染。
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset PYTHONHOME PYTHONPATH CONDA_PREFIX CONDA_DEFAULT_ENV 2>/dev/null || true

if [[ ! -f "${ROS_SETUP}" ]]; then
  echo "错误：未找到 ${ROS_SETUP}" >&2
  exit 1
fi

if [[ ! -f "${WS_SETUP}" ]]; then
  echo "错误：未找到 ${WS_SETUP}，请先编译工作区。" >&2
  exit 1
fi

if pgrep -f 'livox_ros_driver2_node' >/dev/null; then
  echo "错误：MID360S 驱动已经在运行，请勿重复启动。" >&2
  exit 1
fi

# setup.bash 可能引用尚未赋值的变量，加载环境时暂时关闭 nounset。
set +u
source "${ROS_SETUP}"
source "${WS_SETUP}"
set -u

cd "${WORKSPACE}"

echo "启动 MID360S 纯数据节点（无 Foxglove、无 RViz）..."
echo "点云 topic：/livox/lidar"
echo "IMU topic： /livox/imu"
echo "按 Ctrl+C 停止驱动。"

exec ros2 launch livox_ros_driver2 msg_MID360s_launch.py
