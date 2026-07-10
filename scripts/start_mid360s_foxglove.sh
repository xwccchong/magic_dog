#!/usr/bin/env bash

set -Eeuo pipefail

WORKSPACE="/home/nvidia/ws_mid360"
ROS_SETUP="/opt/ros/humble/setup.bash"
WS_SETUP="${WORKSPACE}/install/setup.bash"
FOXGLOVE_PORT="${FOXGLOVE_PORT:-8765}"

# ROS 2 Humble 必须使用 Ubuntu 系统 Python，避免被 Conda 的 python3 覆盖。
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
  echo "错误：livox_ros_driver2_node 已在运行，请先执行 stop_mid360s_foxglove.sh。" >&2
  exit 1
fi

if ss -ltn 2>/dev/null | grep -qE ":${FOXGLOVE_PORT}[[:space:]]"; then
  echo "错误：TCP 端口 ${FOXGLOVE_PORT} 已被占用，请停止已有 Foxglove Bridge 或指定其他端口。" >&2
  exit 1
fi

# setup.bash 可能引用尚未赋值的变量，加载 ROS 环境时暂时关闭 nounset。
set +u
source "${ROS_SETUP}"
source "${WS_SETUP}"
set -u

DRIVER_PID=""
BRIDGE_PID=""

cleanup() {
  trap - EXIT INT TERM
  echo
  echo "正在停止 MID360S 驱动和 Foxglove Bridge..."

  if [[ -n "${BRIDGE_PID}" ]] && kill -0 "${BRIDGE_PID}" 2>/dev/null; then
    kill -INT "${BRIDGE_PID}" 2>/dev/null || true
  fi
  if [[ -n "${DRIVER_PID}" ]] && kill -0 "${DRIVER_PID}" 2>/dev/null; then
    kill -INT "${DRIVER_PID}" 2>/dev/null || true
  fi

  wait "${BRIDGE_PID}" 2>/dev/null || true
  wait "${DRIVER_PID}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "启动 MID360S 驱动（PointCloud2，配置发布频率由 launch 文件决定）..."
ros2 launch livox_ros_driver2 msg_MID360s_launch.py &
DRIVER_PID=$!

sleep 2
if ! kill -0 "${DRIVER_PID}" 2>/dev/null; then
  echo "错误：MID360S 驱动启动失败。" >&2
  wait "${DRIVER_PID}" || true
  exit 1
fi

echo "启动 Foxglove Bridge：0.0.0.0:${FOXGLOVE_PORT}"
ros2 launch foxglove_bridge foxglove_bridge_launch.xml \
  address:=0.0.0.0 \
  port:="${FOXGLOVE_PORT}" &
BRIDGE_PID=$!

WIFI_IP="$(ip -4 -o addr show dev wlP1p1s0 2>/dev/null | awk '{split($4, address, "/"); print address[1]; exit}')"
WIFI_IP="${WIFI_IP:-JETSON_WIFI_IP}"

echo
echo "Foxglove 连接地址：ws://${WIFI_IP}:${FOXGLOVE_PORT}"
echo "点云 topic：/livox/lidar"
echo "IMU topic： /livox/imu"
echo "按 Ctrl+C 同时停止两个进程。"
echo

# 任一进程异常退出时，cleanup 会停止另一个进程。
wait -n "${DRIVER_PID}" "${BRIDGE_PID}"
