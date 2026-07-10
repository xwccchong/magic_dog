# Livox MID360S 在 ARM64 + Ubuntu 22.04 + ROS 2 Humble 上的部署记录

本文记录在与当前控制盒相同的系统上，从零部署一台新的 Livox MID360S，包括 SDK 和 ROS 2
驱动编译、雷达出厂地址识别、使用 SDK 修改雷达 IP、ROS 配置、启动验证和常见故障排查。

## 1. 最终网络规划

| 设备 | 接口 | 静态地址 | 子网掩码 | 网关 |
| --- | --- | --- | --- | --- |
| ARM 控制盒 | `eno1` | `192.168.123.50` | `255.255.255.0` | 可留空 |
| MID360S | 雷达网口 | `192.168.123.20` | `255.255.255.0` | `192.168.123.1` |

每次只连接一台尚未配置的新雷达。如果多台雷达都使用 `192.168.123.20`，不能同时接入同一网络，
否则会发生 IP 冲突。多雷达场景必须为每台雷达分配不同地址。

根据《Livox Mid-360S 用户手册》第 3.3 节：

- 出厂 IP 为 `192.168.1.1XX`，其中 `XX` 是产品 SN 最后两位数字；
- 出厂子网掩码为 `255.255.255.0`；
- 出厂网关为 `192.168.1.1`；
- 首次直连时，电脑推荐使用 `192.168.1.50`；
- 雷达使用普通以太网，不得将 RJ-45 接头连接到 PoE 设备。

例如 SN 最后两位是 `39`，出厂 IP 就是 `192.168.1.139`。

## 2. 软件和目录

验证环境：

```text
CPU 架构：aarch64 / ARM64
操作系统：Ubuntu 22.04
ROS 版本：ROS 2 Humble
工作区：  /home/nvidia/ws_mid360
SDK：     /home/nvidia/ws_mid360/Livox-SDK2
驱动：    /home/nvidia/ws_mid360/src/livox_ros_driver2
```

确认系统：

```bash
uname -m
lsb_release -ds
printenv ROS_DISTRO
```

应分别看到 `aarch64`、Ubuntu 22.04 和 `humble`。所有编译命令都在普通系统终端执行，不使用
Conda 环境。

### 获取源码

如果是全新安装且尚未复制当前工作区，按以下目录结构克隆官方源码：

```bash
mkdir -p /home/nvidia/ws_mid360/src
cd /home/nvidia/ws_mid360
git clone https://github.com/Livox-SDK/Livox-SDK2.git
cd /home/nvidia/ws_mid360/src
git clone https://github.com/Livox-SDK/livox_ros_driver2.git
```

如果 `Livox-SDK2` 和 `src/livox_ros_driver2` 已经存在，不要重复克隆。官方 Livox-SDK2 仓库
默认不包含本文使用的 `set_lidar_ip` 工具；部署新控制盒时，建议复制当前已经修改好的整个
`ws_mid360`，或者将当前的 `Livox-SDK2/samples/set_lidar_ip` 目录及对应 CMake 修改一并复制。

## 3. 安装编译依赖

确认 ROS 2 Humble 已安装，然后执行：

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y build-essential cmake git libapr1-dev libpcl-dev \
  python3-colcon-common-extensions python3-rosdep
```

首次使用 `rosdep` 时执行：

```bash
sudo rosdep init
rosdep update
```

如果提示 sources list 已存在，说明 `rosdep init` 已经执行过，可以忽略该步。安装 ROS 包依赖：

```bash
cd /home/nvidia/ws_mid360
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
```

## 4. 编译并安装 Livox-SDK2

ROS 驱动会从 `/usr/local/lib` 查找 SDK 静态库，因此需要安装 SDK：

```bash
cd /home/nvidia/ws_mid360/Livox-SDK2
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j2
sudo make install
sudo ldconfig
```

`-j2` 对内存较小的 ARM 控制盒更稳。如果确认内存充足，可以用全部 CPU 核心加快编译：

```bash
make -j"$(nproc)"
```

SDK 构建目录固定为 `Livox-SDK2/build`，不会被 ROS 驱动的 `build.sh` 删除。

检查安装结果：

```bash
ls -l /usr/local/lib/liblivox_lidar_sdk_*
ls -l /usr/local/include/livox_lidar_*.h
```

## 5. 编译 ROS 2 驱动

驱动提供了 Humble 构建脚本：

```bash
cd /home/nvidia/ws_mid360
source /opt/ros/humble/setup.bash
./src/livox_ros_driver2/build.sh humble
```

注意：该脚本会删除工作区原来的 `build/`、`install/` 和 `devel/`。不要在这些目录中保存自己的
文件，但不会删除 `Livox-SDK2/build`。编译完成后：

```bash
cd /home/nvidia/ws_mid360
source install/setup.bash
ros2 pkg executables livox_ros_driver2
```

应能看到 `livox_ros_driver2_node`。

## 6. 编译 SDK 改 IP 工具

本工作区已在 `Livox-SDK2/samples/set_lidar_ip` 中加入定向改 IP 工具。它与 SDK 共用
`Livox-SDK2/build`，ROS 驱动重新编译时不会将它清除：

```bash
cd /home/nvidia/ws_mid360/Livox-SDK2/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make set_lidar_ip -j2
```

生成文件：

```text
/home/nvidia/ws_mid360/Livox-SDK2/build/samples/set_lidar_ip/set_lidar_ip
```

工具只会修改命令行指定的当前 IP，并检查设备类型必须为 MID360S，避免误修改网络中的其他
Livox 设备。

## 7. 连接新雷达并确认出厂 IP

1. 只连接这一台新 MID360S；
2. 将雷达 RJ-45 接到控制盒 `eno1`；
3. 按手册要求正确供电，等待启动完成；
4. 不要连接 PoE；
5. 查看雷达标签上的 SN，按最后两位推算出厂 IP。

也可以不依赖 SN，直接观察雷达广播：

```bash
sudo tcpdump -ni eno1 'udp port 56000 or udp port 56200'
```

可能看到：

```text
192.168.1.139.56000 > 255.255.255.255.56000
192.168.1.139.56200 > 255.255.255.255.56201
```

此时出厂 IP 就是 `192.168.1.139`。按 `Ctrl+C` 退出抓包。

## 8. 临时建立出厂网段通信

- 现在的情况是，无线网卡对应ip为`192.168.1.xx`，与有线网口会冲突，所以需要临时建立网段

以下示例假设雷达出厂 IP 为 `192.168.1.139`。新雷达地址不同时，替换命令中的 `.139`。

先停止可能残留的驱动，避免 UDP 端口冲突：

```bash
sudo pkill -f livox_ros_driver2_node || true
```

给 `eno1` 增加手册推荐的临时地址：

```bash
sudo ip addr add 192.168.1.50/32 dev eno1
```

如果返回 `RTNETLINK answers: File exists`，表示地址已经存在，不是故障。

当 Wi-Fi 也使用 `192.168.1.0/24` 时，必须增加到雷达的专用路由，否则数据可能走 Wi-Fi：

```bash
sudo ip route replace 192.168.1.139/32 dev eno1 src 192.168.1.50
ip route get 192.168.1.139
```

正确结果应包含：

```text
192.168.1.139 dev eno1 src 192.168.1.50
```

改 IP 工具使用的主机配置文件是：

```text
Livox-SDK2/samples/set_lidar_ip/mid360s_config.json
```

其中 `host_ip` 应保持为 `192.168.1.50`。

## 9. 将雷达改为 192.168.123.20

这是一次性配置操作。确认网络里只有目标雷达后执行：

```bash
cd /home/nvidia/ws_mid360
sudo ./Livox-SDK2/build/samples/set_lidar_ip/set_lidar_ip \
  Livox-SDK2/samples/set_lidar_ip/mid360s_config.json \
  192.168.1.139 \
  192.168.123.20 \
  255.255.255.0 \
  192.168.123.1
```

成功输出应包含：

```text
Discovered LiDAR: type=35
Matched MID360s at 192.168.1.139
Set-IP response: ret_code=0, error_key=0
IP configuration accepted: 192.168.123.20
Reboot request accepted
```

如果重启请求没有被确认，断开雷达电源，等待 5 秒后重新上电。等待约 15 秒，再检查新地址：

```bash
ping -I eno1 -c 3 192.168.123.20
ip neigh show dev eno1
sudo timeout 10 tcpdump -ni eno1 'host 192.168.123.20'
```

部分设备可能不响应 ping；邻居表中出现雷达 MAC，或者抓到 `.20` 发出的 UDP 数据，都能证明
新地址已经生效。

确认成功后删除临时出厂网段配置：

```bash
sudo ip route del 192.168.1.139/32 dev eno1
sudo ip addr del 192.168.1.50/32 dev eno1
```

## 10. 配置控制盒有线网口

控制盒 `eno1` 最终应为：

```text
192.168.123.50/24
```

检查：

```bash
ip -br addr show eno1
ip route get 192.168.123.20
```

正确路由应包含：

```text
192.168.123.20 dev eno1 src 192.168.123.50
```

如果尚未配置，可以在 Ubuntu“设置 → 网络 → 有线 → IPv4”中选择“手动”，填写：

```text
地址：192.168.123.50
掩码：255.255.255.0
网关：留空
```

设置完成后重新连接有线网卡。

## 11. 配置 ROS 驱动

编辑：

```text
/home/nvidia/ws_mid360/src/livox_ros_driver2/config/MID360s_config.json
```

关键内容为：

```json
"host_ip": "192.168.123.50"
```

以及：

```json
"ip": "192.168.123.20"
```

需要标准 ROS 2 点云消息时，检查：

```text
/home/nvidia/ws_mid360/src/livox_ros_driver2/launch_ROS2/msg_MID360s_launch.py
```

其中应为：

```python
xfer_format = 0
```

含义：

- `0`：发布 `sensor_msgs/msg/PointCloud2`，包含 Livox 扩展字段；
- `1`：发布 Livox 自定义点云消息。

修改源码配置或 launch 文件后重新编译驱动：

```bash
cd /home/nvidia/ws_mid360
source /opt/ros/humble/setup.bash
./src/livox_ros_driver2/build.sh humble
```

这不会删除 `Livox-SDK2/build` 中的 SDK 和改 IP 工具。

## 12. 启动和验证

终端 1：

```bash
cd /home/nvidia/ws_mid360
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch livox_ros_driver2 msg_MID360s_launch.py
```

终端 2：

```bash
source /opt/ros/humble/setup.bash
source /home/nvidia/ws_mid360/install/setup.bash
ros2 node list
ros2 topic list
ros2 topic type /livox/lidar
ros2 topic hz /livox/lidar
ros2 topic echo /livox/imu --once
```

预期至少出现：

```text
/livox/lidar
/livox/imu
```

当 `xfer_format = 0` 时，点云 topic 类型应为：

```text
sensor_msgs/msg/PointCloud2
```

如需 RViz：

```bash
ros2 launch livox_ros_driver2 rviz_MID360s_launch.py
```

在 RViz 中将 Fixed Frame 设置为 `livox_frame`。

## 13. 常见故障排查

### 驱动初始化成功但没有 topic

通常表示 SDK 没有发现配置文件指定的雷达。依次检查：

```bash
ip -br addr show eno1
ip route get 192.168.123.20
ip neigh show dev eno1
sudo tcpdump -ni eno1 'host 192.168.123.20'
```

JSON 中的 `"ip"` 表示“雷达当前 IP”，不会自动修改雷达 IP。

### 没运行 launch 却看到本机 56000 广播

检查残留进程和端口：

```bash
ps -ef | grep livox_ros_driver2_node
sudo ss -ulpn | grep -E ':(56000|56101|56201|56301|56401|56501)\b'
```

清理：

```bash
sudo pkill -f livox_ros_driver2_node
```

### `ros2 topic list` 显示旧节点或旧 topic

```bash
ros2 daemon stop
ros2 daemon start
ros2 topic list
```

### 雷达地址仍是出厂地址

先按 SN 规则和抓包确认真实旧 IP，再重新添加 `/32` 路由并运行改 IP 工具。若工具已经返回
`ret_code=0, error_key=0`，但雷达仍广播旧地址，给雷达断电 5 秒后重新上电。

### 防火墙影响 UDP

仅用于定位问题时，可以检查：

```bash
sudo ufw status
```

Livox MID360S 使用 UDP 广播和配置文件中 `56000` 至 `56501` 一组端口。生产环境应按实际安全
策略放行对应接口和端口，不建议长期无条件关闭防火墙。

## 14. 新雷达部署速查

1. 安装并编译 SDK、ROS 驱动；
2. 编译 `set_lidar_ip`；
3. 单独连接新雷达，通过 SN 或 `tcpdump` 找到出厂 IP；
4. 为 `eno1` 添加 `192.168.1.50/32` 和到雷达的 `/32` 路由；
5. 使用 `set_lidar_ip` 将雷达改为 `192.168.123.20`；
6. 重启雷达并确认 `.20` UDP 数据；
7. 删除临时 `.1.x` 地址和路由；
8. 确认控制盒为 `192.168.123.50/24`；
9. 配置 `MID360s_config.json`；
10. 启动驱动并检查 `/livox/lidar` 和 `/livox/imu`。


# 雷达进程启动

- 常规启动脚本：`/home/nvidia/ws_mid360/scripts/start_mid360s.sh`
- 使用foxglove可视化启动脚本：`FOXGLOVE_PORT=8766 /home/nvidia/ws_mid360/scripts/start_mid360s_foxglove.sh`
- 关闭foxglove可视化脚本：`/home/nvidia/ws_mid360/scripts/stop_mid360s_foxglove.sh`

