#!/bin/bash

# --- 1. 初始化 Conda 环境 ---
# 这一步是为了让脚本能在非交互式 Shell 中识别 conda 命令
CONDA_PATH=$(conda info --base 2>/dev/null)
if [ -z "$CONDA_PATH" ]; then
    # 如果找不到 conda，尝试常见的默认安装路径
    source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null
else
    source "$CONDA_PATH/etc/profile.d/conda.sh"
fi

# 激活 go2 环境
conda activate go2

# --- 2. 设置项目根目录 ---
# 这一步非常重要！它解决了你之前遇到的“找不到模块”的问题
# 将 SDK 的根目录加入 Python 搜索路径
export PYTHONPATH=$PYTHONPATH:/home/unitree/unitree_sdk2_python

# --- 3. 运行程序 ---
echo "---------------------------------------"
echo "正在启动 Unitree HW Check..."
echo "当前环境: $CONDA_DEFAULT_ENV"
echo "---------------------------------------"

python /home/unitree/unitree_sdk2_python/agent/level1/hw_check.py