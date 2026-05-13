# conda activate go2_navi
source /opt/ros/foxy/setup.bash 
source ~/unitree_ros2/setup.sh
export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds
export PYTHONPATH=$PYTHONPATH:~/unitree_sdk2_python
python /home/unitree/unitree_sdk2_python/navi_update/client_v8.py