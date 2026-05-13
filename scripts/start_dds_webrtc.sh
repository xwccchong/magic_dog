#!/bin/bash
# ========================================
# Unitree Go2 DDS / WebRTC 网络一键配置脚本
# ========================================
# 执行位置：狗本体 Jetson 终端
#
# 默认配置：
#   狗主控网口: eth0
#   服务器侧网口: wlan0
#   Jetson DDS IP: 172.50.1.125
#   服务器 DDS Peer: 172.50.0.187
#
# 可临时覆盖：
#   DOG_IFACE=eth1 SERVER_IFACE=wlan0 DDS_LOCAL_IP=172.50.1.125 DDS_PEER_IP=172.50.0.187 ./start_dds_webrtc.sh
# ========================================

set -euo pipefail

DOG_IFACE="${DOG_IFACE:-eth0}"
SERVER_IFACE="${SERVER_IFACE:-wlan0}"
DDS_LOCAL_IP="${DDS_LOCAL_IP:-172.50.1.125}"
DDS_PEER_IP="${DDS_PEER_IP:-172.50.0.187}"

ROS_FOXY_SETUP="${ROS_FOXY_SETUP:-/opt/ros/foxy/setup.bash}"
UNITREE_ROS2_SETUP="${UNITREE_ROS2_SETUP:-$HOME/unitree_ros2/setup.sh}"
CYCLONEDDS_XML="${CYCLONEDDS_XML:-/tmp/cyclonedds_pc3.xml}"
DDS_ENV_FILE="${DDS_ENV_FILE:-/tmp/unitree_dds_webrtc_env.sh}"

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "错误: 未找到命令 $1"
        exit 1
    fi
}

source_setup() {
    local setup_file="$1"
    local nounset_enabled=0

    if [[ $- == *u* ]]; then
        nounset_enabled=1
        set +u
    fi

    source "$setup_file"

    if [ "$nounset_enabled" -eq 1 ]; then
        set -u
    fi
}

add_iptables_rule() {
    local table="$1"
    shift

    if sudo iptables -t "$table" -C "$@" 2>/dev/null; then
        echo "已存在 iptables($table): $*"
    else
        sudo iptables -t "$table" -A "$@"
        echo "已添加 iptables($table): $*"
    fi
}

add_filter_rule() {
    if sudo iptables -C "$@" 2>/dev/null; then
        echo "已存在 iptables(filter): $*"
    else
        sudo iptables -A "$@"
        echo "已添加 iptables(filter): $*"
    fi
}

require_command sudo
require_command iptables

echo "========================================"
echo "   配置 Jetson 转发与 DDS 环境"
echo "========================================"
echo "狗主控网口:      $DOG_IFACE"
echo "服务器侧网口:    $SERVER_IFACE"
echo "Jetson DDS IP:   $DDS_LOCAL_IP"
echo "服务器 DDS Peer: $DDS_PEER_IP"
echo "========================================"

echo ">>> [1/4] 开启 IPv4 转发"
sudo sysctl -w net.ipv4.ip_forward=1

echo ">>> [2/4] 配置 NAT / FORWARD 规则"
add_iptables_rule nat POSTROUTING -o "$DOG_IFACE" -j MASQUERADE
add_filter_rule FORWARD -i "$SERVER_IFACE" -o "$DOG_IFACE" -j ACCEPT
add_filter_rule FORWARD -i "$DOG_IFACE" -o "$SERVER_IFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT

echo ">>> [3/4] 生成 CycloneDDS 配置"
cat > "$CYCLONEDDS_XML" <<EOF
<CycloneDDS>
  <Domain>
    <General>
      <NetworkInterfaceAddress>$DDS_LOCAL_IP</NetworkInterfaceAddress>
      <AllowMulticast>true</AllowMulticast>
    </General>
    <Discovery>
      <Peers>
        <Peer Address="$DDS_PEER_IP"/>
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
EOF

cat > "$DDS_ENV_FILE" <<EOF
source "$ROS_FOXY_SETUP"
source "$UNITREE_ROS2_SETUP"
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file://$CYCLONEDDS_XML
EOF

if [ ! -f "$ROS_FOXY_SETUP" ]; then
    echo "错误: 找不到 $ROS_FOXY_SETUP"
    exit 1
fi

if [ ! -f "$UNITREE_ROS2_SETUP" ]; then
    echo "错误: 找不到 $UNITREE_ROS2_SETUP"
    exit 1
fi

echo ">>> [4/4] 加载 DDS 环境并重启 ros2 daemon"
source_setup "$ROS_FOXY_SETUP"
source_setup "$UNITREE_ROS2_SETUP"

export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="file://$CYCLONEDDS_XML"

require_command ros2

ros2 daemon stop || true
ros2 daemon start

echo "========================================"
echo "DDS / WebRTC 网络配置已执行。"
echo ""
echo "CycloneDDS 配置: $CYCLONEDDS_XML"
echo "DDS 环境文件:    $DDS_ENV_FILE"
echo ""
echo "如果要让新终端继承同一 DDS 环境，请执行："
echo "  source $DDS_ENV_FILE"
echo "========================================"
