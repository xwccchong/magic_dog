#!/bin/bash
# ========================================
# Unitree Go2 SLAM 独立 Tmux 会话启动脚本
# ========================================
# 功能：为每个任务创建完全独立的 tmux 会话，不切分屏幕。
# 依次启动并等待。
# ========================================

# ==================== 配置区域 ====================
SLAM_DIR="/unitree/module/unitree_slam/bin"
CONDA_ENV="unitree_slam_lidar"
LIDAR_TYPE="mid360"  # 可选: mid360 或 xt16

# 定义三个独立的 Session 名称
SESS_SERVER="go2_slam"
SESS_LIDAR="go2_lidar"
SESS_RELOC="go2_relocation"

# 启动间隔等待时间（秒），确保上一进程完全启动
WAIT_TIME=5
# ==================== 配置结束 ====================

# 1. 检查是否安装了 tmux
if ! command -v tmux &> /dev/null; then
    echo "⚠️ 错误: 未检测到 tmux，请先执行 sudo apt install tmux"
    exit 1
fi

# 2. 清理可能残留的同名旧会话 (防止重复执行脚本导致冲突)
tmux kill-session -t $SESS_SERVER 2>/dev/null
tmux kill-session -t $SESS_LIDAR 2>/dev/null
tmux kill-session -t $SESS_RELOC 2>/dev/null

echo "========================================"
echo "   启动 SLAM 系统 (独立后台进程模式) "
echo "========================================"

# ----------------- 进程 1: SLAM 服务 -----------------
echo ">>> [1/3] 正在启动 SLAM 服务 (会话名: $SESS_SERVER)..."
tmux new-session -d -s $SESS_SERVER
tmux send-keys -t $SESS_SERVER "source /opt/ros/noetic/setup.bash" C-m
tmux send-keys -t $SESS_SERVER "source ~/miniconda3/etc/profile.d/conda.sh" C-m
tmux send-keys -t $SESS_SERVER "conda activate $CONDA_ENV" C-m
tmux send-keys -t $SESS_SERVER "export LD_LIBRARY_PATH=\$CONDA_PREFIX/lib:\$LD_LIBRARY_PATH" C-m
tmux send-keys -t $SESS_SERVER "cd $SLAM_DIR && ./unitree_slam" C-m

echo "    ⏳ 等待 $WAIT_TIME 秒，确保 SLAM 核心节点加载完毕..."
sleep $WAIT_TIME

# ----------------- 进程 2: 雷达驱动 -----------------
echo ">>> [2/3] 正在启动雷达驱动 (会话名: $SESS_LIDAR)..."
tmux new-session -d -s $SESS_LIDAR
tmux send-keys -t $SESS_LIDAR "source /opt/ros/noetic/setup.bash" C-m
tmux send-keys -t $SESS_LIDAR "cd $SLAM_DIR && ./${LIDAR_TYPE}_driver" C-m

echo "    ⏳ 等待 $WAIT_TIME 秒，确保雷达数据流建立..."
sleep $WAIT_TIME

# ----------------- 进程 3: 重定位程序 -----------------
echo ">>> [3/3] 正在启动重定位程序 (会话名: $SESS_RELOC)..."
tmux new-session -d -s $SESS_RELOC
tmux send-keys -t $SESS_RELOC "source /opt/ros/noetic/setup.bash" C-m
tmux send-keys -t $SESS_RELOC "cd $SLAM_DIR && ./keyDemo_changemap eth0 /home/unitree/maps/kitchen.pcd" C-m

echo "    ⏳ 等待 3 秒启动控制台..."
sleep 3

echo "========================================"
echo "✅ 所有组件已在独立的后台成功运行！"
echo ""
echo "【如何进行重定位？】"
echo "  脚本将在 3 秒后自动进入重定位界面，请直接按 'a' 键。"
echo "  按完之后如果想退出来，请按 Ctrl+B，松开后再按 D。"
echo ""
echo "【如何单独查看某个进程的报错？】"
echo "  查看 SLAM服务: tmux attach -t $SESS_SERVER"
echo "  查看 雷达驱动: tmux attach -t $SESS_LIDAR"
echo "  查看 重定位  : tmux attach -t $SESS_RELOC"
echo "========================================"

sleep 3

# 自动把当前屏幕切入“重定位”那个会话，方便你按 a 键
tmux attach-session -t $SESS_RELOC