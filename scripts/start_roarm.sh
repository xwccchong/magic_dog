#!/bin/bash

# 定义你的容器名称
CONTAINER_NAME="roarm_gpu_env"

echo "========================================"
echo "  RoArm 服务端后台自动化启动脚本"
echo "========================================"

# ==========================================
# 1. 容器状态检测与激活
# ==========================================
if [ "$(docker ps -q -f status=running -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "✅ 容器 [${CONTAINER_NAME}] 已经在运行中."
elif [ "$(docker ps -aq -f status=exited -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "🔄 容器 [${CONTAINER_NAME}] 休眠中，正在唤醒..."
    docker start ${CONTAINER_NAME}
else
    echo "❌ 错误: 找不到名为 [${CONTAINER_NAME}] 的容器！请检查容器名称。"
    exit 1
fi

# ==========================================
# 2. 清理环境 (防止你重复运行脚本导致进程冲突)
# ==========================================
echo "🧹 正在清理可能遗留的 ROS 2 进程..."
docker exec ${CONTAINER_NAME} bash -c "pkill -9 -f ros2 || true"
sleep 2 # 等待进程彻底死亡

# ==========================================
# 3. 环境变量拼装 (每次 exec 都要重新 source)
# ==========================================
# 注意：这里默认加上了你之前配置的 M3 型号和 42 号隔离频道，防止报错
ENV_SETUP="source /opt/ros/humble/setup.bash && source /workspace/roarm_ws/roarm_ws/install/setup.bash && export ROARM_MODEL=roarm_m3 && export ROS_DOMAIN_ID=42 && cd /workspace/roarm_ws/roarm_ws"


# ==========================================
# 4. 后台启动核心节点
# ==========================================
echo "🚀 正在启动 MoveIt 规划节点 (无头静默模式)..."
# 使用 -d 参数让其在后台运行，并传入 use_rviz:=False
docker exec -d ${CONTAINER_NAME} bash -c "${ENV_SETUP} && ros2 launch roarm_moveit_cmd command_control.launch.py use_rviz:=False"

# 给 MoveIt 大脑一点启动的缓冲时间
sleep 3 

echo "🦾 正在连接串口并启动底层硬件驱动..."
# 修复了你之前见过的 deprecated 警告，改用标准的参数传递格式
docker exec -d ${CONTAINER_NAME} bash -c "${ENV_SETUP} && ros2 run roarm_driver roarm_driver --ros-args -p serial_port:=/dev/ttyUSB0"

echo "========================================"
echo "🎉 前置准备工作已全部在后台启动完毕！"
echo "你可以随时使用以下指令进入容器进行开发："
echo "docker exec -it ${CONTAINER_NAME} /bin/bash"
echo "========================================"