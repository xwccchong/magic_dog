# conda activate go2_navi
# /home/unitree/unitree_sdk2_python/example/go2/high_level/go2_arm/server.sh
# v7 版本，取消了两个模式
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2/setup.sh
export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds
export PYTHONPATH=$PYTHONPATH:~/unitree_sdk2_python
python /home/unitree/unitree_sdk2_python/navi_update/server_v8.py