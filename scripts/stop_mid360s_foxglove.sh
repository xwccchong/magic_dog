#!/usr/bin/env bash

set -u

echo "停止 MID360S 驱动..."
pkill -INT -f 'livox_ros_driver2_node' 2>/dev/null || true

echo "停止 Foxglove Bridge..."
pkill -INT -f '/foxglove_bridge|foxglove_bridge/foxglove_bridge' 2>/dev/null || true

sleep 2

if pgrep -f 'livox_ros_driver2_node|foxglove_bridge/foxglove_bridge' >/dev/null; then
  echo "仍有相关进程未退出，请使用 ps -ef 检查。" >&2
  exit 1
fi

echo "已停止。"
