#!/bin/bash
# 测试机器狗头部相机录制

# 设置 ROS2 环境
source /opt/ros/foxy/setup.bash
source /home/unitree/unitree_ros2/cyclonedds_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# 设置 Conda 环境
source /home/unitree/miniconda3/etc/profile.d/conda.sh
conda activate go2

# 运行测试
cd /home/unitree/unitree_sdk2_python/agent/level2
python3 mp_front_camera_recorder.py
