# docker配置文件
https://github.com/unitreerobotics/unitree_ros2/blob/master/.devcontainer/Dockerfile-humble
模型请输出 ：{"chat_reply": "考拉巡逻队出发！", "item": "none", "action_plan": [{"action": "anomaly_detection"}]}
# humble 环境搭建

docker run -it \
  --name unitree_humble_env \
  --network host \
  --privileged \
  --runtime nvidia \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v /home/go2/roarm_workspace:/workspace/roarm_ws \
  unitree_humble_dev \
  zsh

docker restart unitree_humble_env
docker start unitree_humble_env
docker exec -it unitree_humble_env zsh

export http_proxy="http://172.50.1.50:7897"
export https_proxy="http://172.50.1.50:7897"

# 测试代码
cd /workspace/roarm_ws/roarm_ws-ros2-humble/src/control
python3 move_waypoints.py

# 控制
roarm ros的dds是 ros2 id是99，要访问就一定要配置
```
# 设置你的专属局域网频道（比如 42，你可以选 1-100 之间的任意数字）
export ROS_DOMAIN_ID=99

cd /workspace/roarm_ws/roarm_ws
xhost +local:root
export DISPLAY=:0

# 启动基本连接
ros2 run roarm_driver roarm_driver serial_port:=/dev/ttyUSB0
xvfb-run -a ros2 launch roarm_moveit_cmd command_control.launch.py
# 启动驱动
# 发布信息节点启动
ros2 launch roarm_description display.launch.py
# 启动可视化
ros2 launch roarm_description display.launch.py use_rviz:=True gui:=True
# 读取关节信息，驱动机械臂移动节点启动
ros2 run roarm_driver roarm_driver serial_port:=/dev/ttyUSB0

# rviz2+moveit规划 控制机械臂
# 启动，否则后续无法执行;不要和前面的display进程一起启动
ros2 launch roarm_moveit_cmd command_control.launch.py
# 获取当前机械臂状态
ros2 service call /get_pose_cmd roarm_msgs/srv/GetPoseCmd
# 末端转关节控制
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.3, y: 0, z: 0.1, roll: 0.2, pitch: 0.2, yaw: 0}"
# initial
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.1, y: 0, z: 0.1, roll: 0, pitch: 0.3, yaw: 0}"
# 直立
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.2, y: 0, z: 0.35, roll: 0, pitch: 0, yaw: 0}"
# left right
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.15, y: 0.1, z: 0.35, roll: 0, pitch: 0, yaw: 0}"
# up down
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.2, y: 0, z: 0.25, roll: 0, pitch: 0.3, yaw: 0}"
# 开夹抓（0-1.5）
ros2 topic pub /gripper_cmd std_msgs/msg/Float32  "{data: 0.5}" -1
```

# 查看ros话题内容
ros2 topic echo /joint_states