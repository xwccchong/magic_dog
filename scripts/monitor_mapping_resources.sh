#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${GO2_MONITOR_LOG:-/home/unitree/go2_resource_monitor.log}"
INTERVAL="${GO2_MONITOR_INTERVAL:-5}"
TOP_N="${GO2_MONITOR_TOP_N:-25}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/foxy/setup.bash}"
DDS_ENV_FILE="${DDS_ENV_FILE:-/tmp/unitree_dds_webrtc_env.sh}"
DOG_IFACE="${DOG_IFACE:-eth0}"
SERVER_IFACE="${SERVER_IFACE:-wlan0}"
HZ_SAMPLE_EVERY="${GO2_MONITOR_HZ_SAMPLE_EVERY:-0}"
TOPIC_CHECK_EVERY="${GO2_MONITOR_TOPIC_CHECK_EVERY:-0}"
INFO_TOPICS="${GO2_MONITOR_INFO_TOPICS:-/dog_odom /scan}"
WATCH_TOPICS="${GO2_MONITOR_WATCH_TOPICS:-/dog_odom /scan /unitree/slam_lidar/points /unitree/slam_lidar/imu /tf /tf_static /odom /imu /point_cloud2 /utlidar/voxel_map_compressed /dog_imu_raw}"
UNWANTED_TOPIC_REGEX="${GO2_MONITOR_UNWANTED_TOPIC_REGEX:-uslam|slam_mapping|slam_relocation|lio_sam|dog_imu_raw|point_cloud2|voxel|unitree/slam_lidar}"

source_ros_env() {
  set +u
  if [ -f "$DDS_ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$DDS_ENV_FILE"
  elif [ -f "$ROS_SETUP" ]; then
    # shellcheck disable=SC1090
    source "$ROS_SETUP"
    export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
    export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_cyclonedds_cpp}"
  fi
  set -u
}

echo "===== Go2 resource monitor started at $(date '+%F %T') =====" >> "$LOG_FILE"
echo "interval=${INTERVAL}s top_n=${TOP_N}" >> "$LOG_FILE"
echo "dog_iface=${DOG_IFACE} server_iface=${SERVER_IFACE} topic_check_every=${TOPIC_CHECK_EVERY} hz_sample_every=${HZ_SAMPLE_EVERY}" >> "$LOG_FILE"
echo "watch_topics=${WATCH_TOPICS}" >> "$LOG_FILE"
echo "info_topics=${INFO_TOPICS}" >> "$LOG_FILE"

i=0

while true; do
  i=$((i + 1))
  {
    echo
    echo "===== $(date '+%F %T') ====="
    uptime
    free -h
    df -h /
    echo "--- network address ---"
    ip -brief addr show "$DOG_IFACE" 2>/dev/null || true
    ip -brief addr show "$SERVER_IFACE" 2>/dev/null || true
    echo "--- network counters ---"
    ip -s link show "$DOG_IFACE" 2>/dev/null || true
    ip -s link show "$SERVER_IFACE" 2>/dev/null || true
    echo "--- top cpu ---"
    ps -eo pid,stat,pcpu,pmem,rss,cmd --sort=-pcpu | head -n "$TOP_N"
    echo "--- robot/topic processes ---"
    pgrep -af 'mid360_driver|mid360_to_scan|dog_state_topic_bridge|unitree_slam|keyDemo|slam_toolbox|ros2|dds|webrtc' || true
    echo "--- tmux sessions ---"
    tmux list-sessions 2>/dev/null || true
    if [ "$TOPIC_CHECK_EVERY" -gt 0 ] && [ $((i % TOPIC_CHECK_EVERY)) -eq 0 ]; then
      echo "--- ros topic quick check ---"
      source_ros_env
      if command -v ros2 >/dev/null 2>&1; then
        echo "--- ros topic list watched/unwanted ---"
        timeout 4s ros2 topic list 2>&1 | grep -E "^/(scan|dog_odom|tf|tf_static|odom|imu|unitree/slam_lidar|dog_imu_raw|uslam|unitree/slam_mapping|unitree/slam_relocation|lio_sam|point_cloud2|utlidar/voxel)" || true
        echo "--- unwanted topic check ---"
        timeout 4s ros2 topic list 2>&1 | grep -E "$UNWANTED_TOPIC_REGEX" || true
        echo "--- critical topic info ---"
        for topic in $INFO_TOPICS; do
          echo "### topic_info ${topic}"
          timeout 4s ros2 topic info -v "$topic" 2>&1 || true
        done
        if [ "$HZ_SAMPLE_EVERY" -gt 0 ] && [ $((i % HZ_SAMPLE_EVERY)) -eq 0 ]; then
          echo "--- low-rate topic hz sample ---"
          for topic in /dog_odom /scan; do
            echo "### topic_hz ${topic}"
            timeout 5s ros2 topic hz "$topic" 2>&1 || true
          done
        fi
      else
        echo "ros2 not found after sourcing"
      fi
    fi
    if command -v tegrastats >/dev/null 2>&1; then
      echo "--- tegrastats ---"
      timeout 2s tegrastats --interval 1000 || true
    fi
  } >> "$LOG_FILE" 2>&1
  sleep "$INTERVAL"
done
