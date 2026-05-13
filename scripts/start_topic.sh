#!/bin/bash
# ========================================
# Unitree Go2 minimal server-SLAM topic startup
# ========================================
# Dog-side responsibilities:
#   1. Start MID360 driver so local PointCloud2 is available.
#   2. Convert MID360 PointCloud2 to /scan with a 20 Hz scan_time target.
#      Actual /scan rate depends on MID360 cloud rate and CPU load.
#   3. Publish /dog_odom from rt/sportmodestate at source rate.
#
# Intentionally NOT started:
#   - unitree_slam
#   - keyDemo_changemap
#   - factory mapping / relocation / uslam / lio_sam pipelines
#   - /dog_imu_raw bridge
# ========================================

set -euo pipefail

MID360_BIN_DIR="${MID360_BIN_DIR:-/home/unitree/go2_mid360_bin}"
LIDAR_DRIVER="mid360_driver"
SCRIPT_DIR="/home/unitree/unitree_sdk2_python/scripts"
SCAN_BRIDGE="/home/unitree/go2_workspace/scripts/start_mid360_scan_bridge_light.sh"
DOG_IFACE="${DOG_IFACE:-eth0}"
ODOM_RATE="${DOG_ODOM_RATE:-0}"
ODOM_QOS="${DOG_ODOM_QOS:-best_effort}"
ODOM_QOS_DEPTH="${DOG_ODOM_QOS_DEPTH:-3}"
SCAN_CPUSET="${SCAN_CPUSET:-2-5}"
DOG_ODOM_CPUSET="${DOG_ODOM_CPUSET:-6-7}"

# MID360 LaserScan runtime overrides used by the dog-side /scan bridge.
# Keep these aligned with mapper_params_mid360*.yaml and the saved-map workflow.
MID360_SCAN_OUTPUT_TOPIC="${MID360_SCAN_OUTPUT_TOPIC:-/scan}"
MID360_SCAN_PROCESS_EVERY_NTH_CLOUD="${MID360_SCAN_PROCESS_EVERY_NTH_CLOUD:-1}"
MID360_SCAN_TIME="${MID360_SCAN_TIME:-0.10}"
MID360_SCAN_TARGET_HZ="${MID360_SCAN_TARGET_HZ:-50}"
MID360_SCAN_ANGLE_INCREMENT="${MID360_SCAN_ANGLE_INCREMENT:-0.008726646259971648}"
MID360_SCAN_MIN_HEIGHT="${MID360_SCAN_MIN_HEIGHT:--0.2}"
MID360_SCAN_MAX_HEIGHT="${MID360_SCAN_MAX_HEIGHT:-1.5}"
MID360_SCAN_RANGE_MAX="${MID360_SCAN_RANGE_MAX:-5.0}"
MID360_SCAN_POINT_STRIDE="${MID360_SCAN_POINT_STRIDE:-2}"

SESS_OLD_SLAM="go2_topic_slam"
SESS_LIDAR="go2_topic_mid360"
SESS_SCAN="go2_topic_scan"
SESS_DOG_STATE="go2_topic_dog_state"

WAIT_TIME=3
ODOM_RATE_LABEL="${ODOM_RATE}Hz"

case "$ODOM_RATE" in
    0|0.0|0.00)
        ODOM_RATE_LABEL="source-rate"
        ;;
esac

require_file() {
    if [ ! -e "$1" ]; then
        echo "错误: 找不到 $1"
        exit 1
    fi
}

stop_matching_process() {
    local pattern="$1"
    if pgrep -f "$pattern" >/dev/null 2>&1; then
        echo "停止旧进程: $pattern"
        pkill -f "$pattern" || true
        sleep 1
    fi
}

if ! command -v tmux >/dev/null 2>&1; then
    echo "错误: 未检测到 tmux，请先执行 sudo apt install tmux"
    exit 1
fi

require_file "$MID360_BIN_DIR/$LIDAR_DRIVER"
require_file "$SCRIPT_DIR/dog_state_topic_bridge_light.py"
require_file "$SCAN_BRIDGE"

echo "========================================"
echo "   清理旧 SLAM / Topic 进程"
echo "========================================"
tmux kill-session -t "$SESS_OLD_SLAM" 2>/dev/null || true
tmux kill-session -t "$SESS_LIDAR" 2>/dev/null || true
tmux kill-session -t "$SESS_SCAN" 2>/dev/null || true
tmux kill-session -t "$SESS_DOG_STATE" 2>/dev/null || true

stop_matching_process "lidar_processor.mid360_to_scan_node_light"
stop_matching_process "dog_state_topic_bridge_light.py"

echo "========================================"
echo "   启动 Go2 最小 Topic 进程"
echo "========================================"

echo ">>> [1/3] 启动 MID360 driver: $SESS_LIDAR"
tmux new-session -d -s "$SESS_LIDAR" \
    "bash --noprofile --norc -lc 'set +u; source /opt/ros/noetic/setup.bash; cd \"$MID360_BIN_DIR\"; exec ./\"$LIDAR_DRIVER\"'"

echo "    等待 $WAIT_TIME 秒，确保雷达点云建立..."
sleep "$WAIT_TIME"

echo ">>> [2/3] 启动 MID360 /scan bridge: $SESS_SCAN"
tmux new-session -d -s "$SESS_SCAN" \
    "bash --noprofile --norc -lc 'export MID360_SCAN_OUTPUT_TOPIC="$MID360_SCAN_OUTPUT_TOPIC"; export MID360_SCAN_PROCESS_EVERY_NTH_CLOUD="$MID360_SCAN_PROCESS_EVERY_NTH_CLOUD"; export MID360_SCAN_TIME="$MID360_SCAN_TIME"; export MID360_SCAN_ANGLE_INCREMENT="$MID360_SCAN_ANGLE_INCREMENT"; export MID360_SCAN_MIN_HEIGHT="$MID360_SCAN_MIN_HEIGHT"; export MID360_SCAN_MAX_HEIGHT="$MID360_SCAN_MAX_HEIGHT"; export MID360_SCAN_RANGE_MAX="$MID360_SCAN_RANGE_MAX"; export MID360_SCAN_POINT_STRIDE="$MID360_SCAN_POINT_STRIDE"; if command -v taskset >/dev/null 2>&1; then exec nice -n 10 taskset -c \"$SCAN_CPUSET\" \"$SCAN_BRIDGE\"; else exec nice -n 10 \"$SCAN_BRIDGE\"; fi'"

echo "    等待 $WAIT_TIME 秒，确保 /scan 建立..."
sleep "$WAIT_TIME"

echo ">>> [3/3] 启动 /dog_odom ${ODOM_RATE_LABEL} bridge: $SESS_DOG_STATE"
tmux new-session -d -s "$SESS_DOG_STATE" \
    "bash --noprofile --norc -lc 'set +u; source /opt/ros/foxy/setup.bash; export ROS_DOMAIN_ID=0; export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp; export CYCLONEDDS_URI=file:///tmp/cyclonedds_pc3.xml; export CYCLONEDDS_HOME=\"\$HOME/cyclonedds_ws/install/cyclonedds\"; export LD_LIBRARY_PATH=\"\$CYCLONEDDS_HOME/lib:\$LD_LIBRARY_PATH\"; cd \"$SCRIPT_DIR\"; if command -v taskset >/dev/null 2>&1; then exec nice -n 5 taskset -c \"$DOG_ODOM_CPUSET\" /usr/bin/python3 dog_state_topic_bridge_light.py --network-interface \"$DOG_IFACE\" --state-topic rt/sportmodestate --publish-rate \"$ODOM_RATE\" --odom-qos \"$ODOM_QOS\" --odom-qos-depth \"$ODOM_QOS_DEPTH\"; else exec nice -n 5 /usr/bin/python3 dog_state_topic_bridge_light.py --network-interface \"$DOG_IFACE\" --state-topic rt/sportmodestate --publish-rate \"$ODOM_RATE\" --odom-qos \"$ODOM_QOS\" --odom-qos-depth \"$ODOM_QOS_DEPTH\"; fi'"

echo "========================================"
echo "最小 topic 进程已启动。"
echo ""
echo "狗端对服务器预期发布："
echo "  /scan       目标最高约 ${MID360_SCAN_TARGET_HZ}Hz, BEST_EFFORT（实际频率取决于 MID360 点云和 CPU 负载）"
echo "  /dog_odom   约 ${ODOM_RATE_LABEL}, ${ODOM_QOS}, depth=${ODOM_QOS_DEPTH}"
echo ""
echo "不再启动 unitree_slam / keyDemo_changemap / 原厂建图重定位程序。"
echo ""
echo "查看日志："
echo "  tmux attach -t $SESS_LIDAR"
echo "  tmux attach -t $SESS_SCAN"
echo "  tmux attach -t $SESS_DOG_STATE"
echo ""
echo "停止这些进程："
echo "  tmux kill-session -t $SESS_LIDAR"
echo "  tmux kill-session -t $SESS_SCAN"
echo "  tmux kill-session -t $SESS_DOG_STATE"
echo "========================================"
