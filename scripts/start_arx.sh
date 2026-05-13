#!/bin/bash
# ========================================
# ARX_X5 机械臂与视觉抓取启动脚本 (独立 Tmux 版)
# ========================================
# 功能：为机械臂控制、CAN通信和YOLO视觉分别创建独立的tmux会话。
# 严格限制在 ROS 1 (Noetic) 环境下运行，防止路径污染。
# ========================================

# ==================== 路径配置区域 ====================
ARX_WS="/home/unitree/ARX_X5/ROS/X5_ws"
CAN_DIR="/home/unitree/ARX_X5/ARX_CAN/arx_can"
CPQ_DIR="/home/unitree/cpq"

# Session 名称定义
SESS_ARX="arx_arm"
SESS_CAN="arx_can"
SESS_YOLO="yolo1grasp2"

WAIT_TIME=5
# ====================================================

# 1. 检查 tmux
if ! command -v tmux &> /dev/null; then
    echo "⚠️ 错误: 未检测到 tmux，请先执行 sudo apt install tmux"
    exit 1
fi

# 2. 清理旧会话
tmux kill-session -t $SESS_CAN 2>/dev/null
tmux kill-session -t $SESS_ARX 2>/dev/null
tmux kill-session -t $SESS_YOLO 2>/dev/null

echo "========================================"
echo "🚀 启动 ARX 机械臂与视觉抓取系统 (Tmux 后台模式)"
echo "========================================"

# ----------------- 进程 1: CAN 通信接口 -----------------
echo ">>> [1/3] 正在启动 CAN 通信接口..."
tmux new-session -d -s $SESS_CAN

tmux send-keys -t $SESS_CAN "3" C-m
sleep 0.5
tmux send-keys -t $SESS_CAN "unset ROS_DISTRO" C-m

tmux send-keys -t $SESS_CAN "source /opt/ros/noetic/setup.bash" C-m
tmux send-keys -t $SESS_CAN "source $ARX_WS/devel/setup.sh" C-m

tmux send-keys -t $SESS_CAN "echo '========== ARX CAN Communication =========='" C-m
tmux send-keys -t $SESS_CAN "cd $CAN_DIR && echo '123' | sudo -S ./arx_can1.sh" C-m

echo "    ⏳ 等待 $WAIT_TIME 秒，确保机械臂控制器加载完毕..."
sleep $WAIT_TIME

# ----------------- 进程 2: ARX 机械臂控制 -----------------
echo ">>> [2/3] 正在启动 ARX 机械臂控制..."
tmux new-session -d -s $SESS_ARX

# 防卡死与环境变量净化
sleep 1
tmux send-keys -t $SESS_ARX "3" C-m
sleep 0.5
tmux send-keys -t $SESS_ARX "unset ROS_DISTRO" C-m

# 加载 ROS 1 Noetic 与工作空间
tmux send-keys -t $SESS_ARX "source /opt/ros/noetic/setup.bash" C-m
tmux send-keys -t $SESS_ARX "cd $ARX_WS && source devel/setup.sh" C-m

# 执行 Launch
tmux send-keys -t $SESS_ARX "echo '========== ARX Controller =========='" C-m
tmux send-keys -t $SESS_ARX "roslaunch arx_x5_controller v2_single_arm.launch" C-m

echo "    ⏳ 等待 $WAIT_TIME 秒..."
sleep $WAIT_TIME

# ----------------- 进程 3: YOLO 视觉控制与抓取 -----------------
echo ">>> [3/3] 正在启动 YOLO 视觉控制与抓取..."
tmux new-session -d -s $SESS_YOLO

tmux send-keys -t $SESS_YOLO "3" C-m
sleep 0.5

# 【关键】严格的环境重置与 Conda 激活 (完全复现你的 control_yolo1grasp2.sh)
tmux send-keys -t $SESS_YOLO "unset ROS_DISTRO" C-m
tmux send-keys -t $SESS_YOLO "unset PYTHONPATH" C-m
tmux send-keys -t $SESS_YOLO "eval \"\$(conda shell.bash hook)\"" C-m
tmux send-keys -t $SESS_YOLO "conda activate arx" C-m

# 加载 ROS 1
tmux send-keys -t $SESS_YOLO "source /opt/ros/noetic/setup.bash" C-m
tmux send-keys -t $SESS_YOLO "source $ARX_WS/devel/setup.sh" C-m

# 注入严格的 PYTHONPATH 和系统库路径
tmux send-keys -t $SESS_YOLO "export PYTHONPATH=\"$ARX_WS/devel/lib/python3/dist-packages:/opt/ros/noetic/lib/python3/dist-packages\"" C-m
tmux send-keys -t $SESS_YOLO "export PATH=\"\$CONDA_PREFIX/bin:\$PATH\"" C-m
tmux send-keys -t $SESS_YOLO "export LD_LIBRARY_PATH=\"\$CONDA_PREFIX/lib:\$LD_LIBRARY_PATH\"" C-m
tmux send-keys -t $SESS_YOLO "export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1" C-m

# 打印验证信息并执行 Python 脚本
tmux send-keys -t $SESS_YOLO "echo '========== YOLO Vision Control =========='" C-m
tmux send-keys -t $SESS_YOLO "echo 'Using Python: \$(which python3)'" C-m
tmux send-keys -t $SESS_YOLO "cd $CPQ_DIR && python control_unitree_yolo1grasp2.py" C-m

echo "    ⏳ 系统启动完成！"
sleep $WAIT_TIME

echo "========================================"
echo "✅ 所有 3 个机械臂与视觉进程已成功运行在后台！"
echo ""
echo "【如何查看对应进程的运行状态与日志？】"
echo "  [1] 机械臂控制: tmux attach -t $SESS_ARX"
echo "  [2] CAN 通信  : tmux attach -t $SESS_CAN"
echo "  [3] 视觉抓取  : tmux attach -t $SESS_YOLO"
echo "========================================"

# 默认切入视觉抓取的终端，方便查看 YOLO 的输出或检测结果
tmux attach-session -t $SESS_YOLO