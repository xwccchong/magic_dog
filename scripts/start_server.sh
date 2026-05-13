#!/bin/bash
# ========================================
# Unitree Go2 服务启动脚本 (完全整合版 v2)
# ========================================

# ==================== 配置区域 ====================
NAVI_DIR="/home/unitree/unitree_sdk2_python/navi_update"
SDK_DIR="/home/unitree/unitree_sdk2_python"

# 定义两个独立的 Session 名称
SESS_SERVER="go2_server"
SESS_CLIENT="go2_client"
CONDA_ENV="go2"

WAIT_TIME=5
# ==================== 配置结束 ====================

if ! command -v tmux &> /dev/null; then
    echo "⚠️ 错误: 未检测到 tmux，请先执行 sudo apt install tmux"
    exit 1
fi

tmux kill-session -t $SESS_SERVER 2>/dev/null
tmux kill-session -t $SESS_CLIENT 2>/dev/null

echo "========================================"
echo "   启动 Go2 语音与任务服务 (后台模式) "
echo "========================================"

# ----------------- 进程 1: Server 语音识别服务 -----------------
echo ">>> [1/2] 正在启动 Server 语音识别服务 (会话名: $SESS_SERVER)..."
tmux new-session -d -s $SESS_SERVER

# 【关键修复】等待bash加载，然后发送 "3" 并回车，跳过 .bashrc 的 fishros 选择菜单！
sleep 1
tmux send-keys -t $SESS_SERVER "3" C-m
sleep 0.5

# 清除父终端残留的 ROS 1 (Noetic) 环境干扰
tmux send-keys -t $SESS_SERVER "unset ROS_DISTRO" C-m

# 环境配置: Conda + ROS 2 Foxy + CycloneDDS + PYTHONPATH
tmux send-keys -t $SESS_SERVER "source /opt/ros/foxy/setup.bash" C-m
tmux send-keys -t $SESS_SERVER "source ~/miniconda3/etc/profile.d/conda.sh && conda activate $CONDA_ENV" C-m
tmux send-keys -t $SESS_SERVER "export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds" C-m
tmux send-keys -t $SESS_SERVER "export PYTHONPATH=\$PYTHONPATH:$SDK_DIR" C-m

# 打印操作提示信息
tmux send-keys -t $SESS_SERVER "clear" C-m
tmux send-keys -t $SESS_SERVER "echo '========== Server 语音识别服务 =========='" C-m
tmux send-keys -t $SESS_SERVER "echo '操作说明:'" C-m
tmux send-keys -t $SESS_SERVER "echo '  正常模式: 语音对话'" C-m
tmux send-keys -t $SESS_SERVER "echo '  按 s: 展览模式 (每40s自动招揽)'" C-m
tmux send-keys -t $SESS_SERVER "echo '  按 t: 手动输入模式'" C-m
tmux send-keys -t $SESS_SERVER "echo '  按 q: 重新回到监听模式'" C-m
tmux send-keys -t $SESS_SERVER "echo '⚠️ 首先说唤醒词 \"考拉二号\" 进行对话'" C-m
tmux send-keys -t $SESS_SERVER "echo '----------------------------------------'" C-m

# 直接执行 Python 脚本
tmux send-keys -t $SESS_SERVER "cd $NAVI_DIR && python server_recon_v8.py" C-m

echo "    ⏳ 等待 $WAIT_TIME 秒，确保 Server 核心节点初始化完毕..."
sleep $WAIT_TIME

# ----------------- 进程 2: Client 任务执行 -----------------
echo ">>> [2/2] 正在启动 Client 任务执行服务 (会话名: $SESS_CLIENT)..."
tmux new-session -d -s $SESS_CLIENT

# 【关键修复】同样跳过 Client 会话中的 fishros 选择菜单
sleep 1
tmux send-keys -t $SESS_CLIENT "3" C-m
sleep 0.5

# 清除父终端残留的 ROS 1 (Noetic) 环境干扰
tmux send-keys -t $SESS_CLIENT "unset ROS_DISTRO" C-m

# 环境配置: Conda + ROS 2 Foxy + CycloneDDS + LD_LIBRARY_PATH + PYTHONPATH
tmux send-keys -t $SESS_CLIENT "source ~/miniconda3/etc/profile.d/conda.sh && conda activate $CONDA_ENV" C-m
tmux send-keys -t $SESS_CLIENT "source /opt/ros/foxy/setup.bash" C-m
tmux send-keys -t $SESS_CLIENT "export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds" C-m
tmux send-keys -t $SESS_CLIENT "export LD_LIBRARY_PATH=\$CYCLONEDDS_HOME/lib:\$LD_LIBRARY_PATH" C-m
tmux send-keys -t $SESS_CLIENT "export PYTHONPATH=\$PYTHONPATH:$SDK_DIR" C-m

# 打印提示并直接执行 Python 脚本
tmux send-keys -t $SESS_CLIENT "clear" C-m
tmux send-keys -t $SESS_CLIENT "echo '========== Client 任务执行 =========='" C-m
tmux send-keys -t $SESS_CLIENT "cd $NAVI_DIR && python client_recon_v8.py" C-m

echo "    ⏳ 等待 2 秒启动控制台..."
sleep 2

echo "========================================"
echo "✅ 服务进程已在独立的后台成功运行！"
echo ""
echo "【如何单独查看某个进程的报错或状态？】"
echo "  查看 Server(语音): tmux attach -t $SESS_SERVER"
echo "  查看 Client(任务): tmux attach -t $SESS_CLIENT"
echo "========================================"

sleep 3
tmux attach-session -t $SESS_SERVER