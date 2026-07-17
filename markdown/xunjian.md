# 机器狗巡检项目

## ‼️ 注意
\* 雷达不要热插拔，要给机器狗断电后再插拔

\* 机器狗的遥控器使用 3D 打印机上的白色充电线充电

\*  Go2 Edu 宇树官方文档：[这里](https://support.unitree.com/home/zh/developer/SLAM%20and%20Navigation_service)

\*有问题 可以提工单 进行人工咨询：https://serviceconsole.unitree.com/index.html#/  

\* 看开发常见问题：https://serviceconsole.unitree.com/#/help/031302

\*麦克风配对：

1.麦克风按配对键2秒，切换到蓝绿灯交替闪烁，再按接收器配对键2秒，都绿灯常亮配对成功

现在已经配对好了，一般时候是先打开狗上的接收器，然后拿着麦克风开机，靠近接收器，等几秒钟自动连接。

2.当麦克风无法收音时，再终端运行 arecord -D hw:2,0 -d 3 -f S24_3LE -r 48000 -c 2 test_wireless.wav 

然后开始说话录音，查看test_wireless.wav 是否有声音

- **这条旧狗的信号输出源被关闭了（问题未知），所以无法外界显示器查看系统**

## 一些基础配置

### docker 容器配置
前提：系统已经安装好了docker

参考`https://github.com/unitreerobotics/unitree_ros2/blob/master/README%20_zh.md`, git 宇树对应的ros仓库

需要给docker内部配置代理，才能从docker源拉取包

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf

# 写入以下配置（请将 127.0.0.1:7890 替换为你实际的代理 IP 和端口）
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:7890"
Environment="HTTPS_PROXY=http://127.0.0.1:7890"
Environment="NO_PROXY=localhost,127.0.0.1"

sudo systemctl daemon-reload
sudo systemctl restart docker

docker build -t unitree_ros2:humble -f .devcontainer/Dockerfile-humble .
```

### 网卡网络配置

查看当前连接名称：nmcli con show

**修改 WiFi 连接的 Metric**：sudo nmcli con mod "your-wifi-name" ipv4.route-metric 100

**重启连接以生效**：

sudo nmcli con down "your-wifi-name"
sudo nmcli con up "your-wifi-name"

可以直接使用网线连接机器狗的jetson板（背部，前面的接口），使用ssh连接机器狗


- 在插网线后，在个人设备中查看是否有网线连接，需要手动设置ip，配置为192.168.123.100（不能是20，161，18结尾）；因为

    机器狗本体内部的ip为192.168.123.161；
    雷达ip为192.168.123.20;
    jetson板ip为192.168.123.18

使用ssh连接: ssh unitree@192.168.123.18;进入之后可以进行网络配置；配置好之后使用ifconfig查看（一般是wlan0对应的ip）


## 基础文件夹列表

- Fastlio 重定位建图

    /home/go2/nav_workspace

- roarm小机械臂控制

    /home/go2/roarm_workspace/roarm_ws-ros2-humble

- 宇树机器狗项目主控（python）

    /home/unitree/unitree_sdk2_python

- 宇树机器狗底层导航等控制（闭源）

    /unitree/module/unitree_slam

- 启动脚本

    /home/unitree/unitree_sdk2_python/scripts

- 修改
    wts.2026.6.4

## 1. 机器狗主控

### 核心文件列表

- 启动脚本：

    bash /home/unitree/unitree_sdk2_python/scripts/start_server.sh

- 核心文件：

    - 多模态信息收集交互：/home/unitree/unitree_sdk2_python/navi_update/server_recon_v8.py

    - 主控进程：/home/unitree/unitree_sdk2_python/navi_update/client_recon_v8.py

    - 任务定义与配置管理：/home/unitree/unitree_sdk2_python/navi_update/task_manager_recon_v4.py

    - 文本转语音：/home/unitree/unitree_sdk2_python/navi_update/tts_v8.py

    - 机器狗导航python外部接口：/home/unitree/unitree_sdk2_python/navi_update/unitree_nav.py

- 每一个机器狗的原子动作都有定义，可以修改，也可以拓展到新的动作

    /home/unitree/unitree_sdk2_python/navi_update/actions

- 程序基本的参数配置

    /home/unitree/unitree_sdk2_python/navi_update/config

    - 异常检测的prompt

        /home/unitree/unitree_sdk2_python/navi_update/config/AD_prompt.txt

    - LLM大脑的prompt，需在这里定义动作链序列，以及基本的模型输出规则

        /home/unitree/unitree_sdk2_python/navi_update/config/llm_prompt_v2.txt

### 启动后tmux列表

- go2_server
- go2_client

## 2. 宇树机器狗底层导航等控制

### 核心文件列表

- 启动脚本：

    bash /home/unitree/unitree_sdk2_python/scripts/start_slam.sh

    需要修改加载地图的路径：tmux send-keys -t $SESS_RELOC "cd $SLAM_DIR && ./keyDemo_changemap eth0 /home/unitree/maps/company_001_level_pro.pcd" C-m

    其中keydemo_changemap 是我在是官方提供的例子 KeyDemo 基础上又写了一版，具体可以参考：[KeyDemo 的使用方法](https://serviceconsole.unitree.com/#/help/03060505)，具体的c++代码修改与编译参考 `/unitree/module/unitree_slam/run.md`

### tmux列表

- go2_slam （这个是导航最基础的，打开之后不要关闭）
- go2_lidar （这个是雷达的进程，也不能关闭）
- go2_relocation (这个是重定位，取点的进程)


## 3. Fastlio 重定位建图

复现的fastlio 项目，使用open3d进行重定位；可以参考github

点云可视化，处理软件使用的是Cloud Compare

也可以查看下方的两个readme（会更集成，更详细些）
```
/home/go2/nav_workspace/README_fastlio_unitree_multi_nav.md
/home/go2/nav_workspace/README_fastlio_unitree_step_scripts.md
```

### 在docker中运行
```
# docker还你家那个创建
docker run -it \
  --name unitree_humble_nav \
  --network host \
  --privileged \
  --runtime nvidia \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v /home/go2/nav_workspace:/workspace/nav_ws \
  unitree_humble_dev \
  zsh

# 进入/重启docker
docker restart unitree_humble_nav
docker start unitree_humble_nav
docker exec -it unitree_humble_nav zsh

# 配置代理（安装库时临时使用）
export http_proxy="http://172.50.1.50:7897"
export https_proxy="http://172.50.1.50:7897"
```

- 启动雷达
    cd /unitree/module/unitree_slam/bin
    ./mid360_driver 

- 启动建图
    使用foxglove进行可视化，支持无头；foxglove中连接机器狗ip即可

    source /workspace/nav_ws/install/setup.zsh
    ros2 launch fast_lio mapping.launch.py


-  检查机器狗是否在发布数据

    ros2 topic hz /unitree/slam_lidar/points
    ros2 topic hz /unitree/slam_lidar/imu

- 检查 FAST_LIO 输出（确保在运行）

    ros2 topic hz /cloud_registered_1
    ros2 topic hz /Odometry_loc

    ros2 service call /map_save std_srvs/srv/Trigger


### 地图倾斜问题
雷达与水平地面有倾角；在建图时是使用的是雷达自身的imu，所以建图的额结果地面是倾斜的，角度就是雷达和水平地面的夹角

由于初始位置在地图的角上面，所以整个地图的z均值是负的或者正的（远不是0），所以就会导致在重定位的时候出现z为-2.74m的情况

现在的模式为：进行两次平面拟合与旋转，然后将目标地面高低拉到0.3m；

- 地图拉平程序（自动匹配算法）

```
# 需要修改为docker容器中对应的路径
/home/go2/nav_workspace/maps/pcd_postprocess_pro.py

# 此外，程序中处理的地图与输出的地图路径记得修改
def main():
    # 示例用法
    input_pcd = "company_000.pcd"
    output_pcd = "company_001_level_pro.pcd"
```

## 4. roarm小机械臂

### docker配置文件（参考宇树官方在机器狗中配置22.04+humble）
https://github.com/unitreerobotics/unitree_ros2/blob/master/.devcontainer/Dockerfile-humble

- humble 环境搭建
```
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
```

- 测试代码

    cd /workspace/roarm_ws/roarm_ws-ros2-humble/src/control
    python3 move_waypoints.py

-  控制

    roarm ros的dds是 ros2 id是99，要访问就一定要配置

    查看usb口号

    ls /dev/tty*

- 远程使用foxglove可视化的时候，本地电脑不要挂代理，不然无法访问

- ‼️ **一定要配置好ros id，避免串台**
```
# 设置你的专属局域网频道（比如 42，你可以选 1-100 之间的任意数字）
export ROS_DOMAIN_ID=99

cd /workspace/roarm_ws/roarm_ws
xhost +local:root
export DISPLAY=:0

```

- **启动基本连接(3个终端启动)**

```
# 终端1
ros2 run roarm_driver roarm_driver serial_port:=/dev/ttyUSB0

# 终端2
ros2 launch roarm_moveit_cmd command_control.launch.py

# 终端3
cd /workspace/roarm_ws/roarm_ws-ros2-humble/src/control
python3 arm_pose_bridge.py 

# xvfb-run -a ros2 launch roarm_moveit_cmd command_control.launch.py
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
# 1象限
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.15, y: -0.08, z: 0.35, roll: 0, pitch: -0.15, yaw: 0}"
# 2象限
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.15, y: 0.08, z: 0.35, roll: 0, pitch: -0.15, yaw: 0}"
# 3象限
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.15, y: 0.08, z: 0.30, roll: 0, pitch: 0.15, yaw: 0}"
# 4象限
ros2 service call /move_joint_cmd roarm_msgs/srv/MoveJointCmd "{x: 0.15, y: -0.08, z: 0.30, roll: 0, pitch: 0.15, yaw: 0}"

# 开夹抓（0-1.5）
ros2 topic pub /gripper_cmd std_msgs/msg/Float32  "{data: 0.5}" -1
```

- 查看ros话题内容
    
    ros2 topic echo /joint_states










