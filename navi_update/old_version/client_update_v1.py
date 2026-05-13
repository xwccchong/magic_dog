# -*- coding: utf-8 -*-
"""
实时语音识别 - Client 接收端
需要安装: pip install websockets
使用方式: python client.py
连接到服务器并接收消息
"""
import asyncio
import websockets
import os
import subprocess
import json
import sys
import logging
import re
sys.path.insert(0, '/home/unitree/dky/go2_python_sdk2')
from play_audio import play_audio
import threading

from task_manager import TaskManager, TaskType
from unitree_nav import AsyncNavigationManager


# 禁用代理（适用于本地连接，避免 SOCKS 代理问题）
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['socks_proxy'] = ''

# 全局导航对象
nav = AsyncNavigationManager()

# 全局 websocket 引用（用于接收 back 消息）
global_websocket = None

# 物品到对象名称和音频文件的映射
item_mapping = {
    "水": {
        "obj_name": "white bottle",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/lc_water_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/lc_water_start.wav"
    },
    "纸": {
        "obj_name": "tissue",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/tissue_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/tissue_start.wav"
    },
    "糖": {
        "obj_name": "cup",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/sugar_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/sugar_start.wav"
    },
    "雨伞": {
        "obj_name": "red umbrella",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/lsl_umbrella_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/lsl_umbrella_start.wav"
    },
    "咖啡": {
        "obj_name": "brown bottle",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/coffee_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/coffee_start.wav"
    },
    "外卖": {
        "obj_name": "brown bag",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/lc_takeout_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/lc_takeout_start.wav"
    },
    "饮料": {
        "obj_name": "white bottle",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/yinliao_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/yinliao_start.wav"
    }
}

# 地点到导航路径点列表的映射
location_poses_mapping = {
    "前台": [
        (2.98671, -0.307209, 0.067685, 0.0051042, -0.121825, -0.0396321, -0.991747),
        # (4.96802, -0.0545474, 0.0722993, -0.0970867, 0.105798, 0.706048, 0.693454),
    ],
    "办公室": [
        # (0.00240726, -0.514558, 0.0382567, 0.0061988, -0.137903, -0.00690807, 0.990402),
        (-1.03291, 2.10079, 0.0331177, 0.111722 , -0.0748998 , -0.851018, -0.507618)
    ],
    "吧台": [
        (1.34411, -2.21261, 0.0486366, 0.079105, 0.0762893, -0.694252, 0.711292)
    ],
    "初始位置": [
        (-0.334, -0.086, -0.044, 0.018, 0.035, 0.012, 0.999)
    ],
    "门口": [
        (7.931, 16.522, -0.005, -0.019, 0.017, 0.999, -0.052)
    ],
    "雨伞架": [
        (6.040, 3.369, 0.028, -0.004, 0.022, 0.701, 0.713)
    ]
}

# 全局变量：存储出发位置
departure_position = None

# 全局任务管理器
task_manager = TaskManager()


# ============================================================
# 机器人动作控制函数（从 neupan 迁移过来）
# ============================================================

async def execute_down_script(location_name=""):
    """
    执行蹲下脚本
    根据位置选择不同的 down 脚本
    """
    if location_name == "门口":
        script_path = "/home/unitree/unitree_sdk2_python/example/go2/high_level/down_door.py"
        print(f"🚪 检测到位置：门口，执行 down_door.py")
    else:
        script_path = "/home/unitree/unitree_sdk2_python/example/go2/high_level/down.py"
        print(f"📍 当前位置：{location_name or '未知'}，执行 down.py")
    
    command = (
        "source ~/miniconda3/etc/profile.d/conda.sh && "
        "conda activate go2_navi && "
        "source /opt/ros/foxy/setup.bash && "
        "source ~/unitree_ros2/setup.sh && "
        "export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds && "
        "export PYTHONPATH=$PYTHONPATH:~/unitree_sdk2_python && "
        f"python {script_path} eth0"
    )
    
    try:
        print(f"⬇️  开始执行蹲下脚本...")
        process = await asyncio.create_subprocess_shell(
            command,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"✓ 蹲下脚本执行成功")
        else:
            print(f"❌ 蹲下脚本执行失败:\n{stderr.decode()}")
    except Exception as e:
        print(f"❌ 执行蹲下脚本出错: {e}")


async def execute_up_script():
    """执行站起来脚本"""
    command = (
        "source ~/miniconda3/etc/profile.d/conda.sh && "
        "conda activate go2_navi && "
        "source /opt/ros/foxy/setup.bash && "
        "source ~/unitree_ros2/setup.sh && "
        "export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds && "
        "export PYTHONPATH=$PYTHONPATH:~/unitree_sdk2_python && "
        "python /home/unitree/unitree_sdk2_python/example/go2/high_level/up.py eth0"
    )
    
    try:
        print(f"⬆️  开始执行站起来脚本...")
        process = await asyncio.create_subprocess_shell(
            command,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"✓ 站起来脚本执行成功")
        else:
            print(f"❌ 站起来脚本执行失败:\n{stderr.decode()}")
    except Exception as e:
        print(f"❌ 执行站起来脚本出错: {e}")


async def send_grasp_target(obj_name):
    """
    发送抓取目标给机械臂
    通过 ROS2 话题 /grasp_target 发送
    """
    command = (
        "source /opt/ros/foxy/setup.bash && "
        f'ros2 topic pub /grasp_target std_msgs/msg/String "{{data: \'{obj_name}\'}}" --once'
    )
    
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        print(f"✓ 抓取目标已发送: {obj_name}")
    except Exception as e:
        print(f"❌ 发送抓取目标失败: {e}")


# ============================================================
# 抓取完整流程
# ============================================================

async def execute_grasp_sequence(item, obj_name, location_name, websocket):
    """
    执行完整的抓取流程:
    1. 蹲下
    2. 发送物体名称给机械臂
    3. 等待机械臂发送 "back" 信号
    4. 站起来
    
    Args:
        item: 物品名称（中文）
        obj_name: 物体识别名称
        location_name: 当前位置名称（用于选择蹲下脚本）
        websocket: WebSocket 连接（用于接收 back 消息）
    """
    print(f"\n{'='*60}")
    print(f"🤖 开始执行抓取流程")
    print(f"   物品: {item} ({obj_name})")
    print(f"   位置: {location_name}")
    print(f"{'='*60}\n")
    
    # ===== 步骤1: 蹲下 =====
    print("📌 步骤1/4: 执行蹲下指令")
    await execute_down_script(location_name)
    print("✓ 蹲下完成")
    await asyncio.sleep(1)  # 等待稳定
    
    # ===== 步骤2: 发送物体名称给机械臂 =====
    print(f"📌 步骤2/4: 发送物体名称 '{obj_name}' 给机械臂")
    await send_grasp_target(obj_name)
    print("✓ 物体名称已发送")
    
    # ===== 步骤3: 等待机械臂发送 "back" 信号 =====
    print("📌 步骤3/4: 等待机械臂完成抓取（'back' 信号）...")
    back_received = await wait_for_back_signal(websocket)
    
    if back_received:
        print("✓ 收到 'back' 信号，机械臂抓取完成")
    else:
        print("⚠️ 等待 'back' 信号超时，继续执行")
    
    await asyncio.sleep(1)  # 等待稳定
    
    # ===== 步骤4: 站起来 =====
    print("📌 步骤4/4: 执行站起来指令")
    await execute_up_script()
    print("✓ 站起来完成")
    await asyncio.sleep(2)  # 等待稳定
    
    print(f"\n{'='*60}")
    print(f"✅ 抓取流程完成: {item}")
    print(f"{'='*60}\n")


async def wait_for_back_signal(websocket, timeout=120):
    """
    等待机械臂发送的 "back" 信号
    在等待期间，仍然可以接收其他消息
    
    Args:
        websocket: WebSocket 连接
        timeout: 超时时间（秒），默认120秒
        
    Returns:
        bool: 是否成功收到 back 信号
    """
    print(f"⏳ 等待 'back' 信号（超时: {timeout}秒）...")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        while True:
            remaining = timeout - (asyncio.get_event_loop().time() - start_time)
            
            if remaining <= 0:
                print(f"⚠️ 等待 'back' 信号超时（{timeout}秒）")
                return False
            
            try:
                message = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=min(remaining, 5.0)  # 每5秒检查一次
                )
                
                print(f"📨 [等待back中] 收到消息: {message}")
                
                if message == "back":
                    return True
                else:
                    # 收到非 back 消息，暂时忽略（或可以存入队列）
                    print(f"⏭️  非 back 消息，继续等待...")
                    
            except asyncio.TimeoutError:
                elapsed = asyncio.get_event_loop().time() - start_time
                print(f"⏳ 仍在等待 'back' 信号... ({elapsed:.0f}/{timeout}秒)")
                continue
                
    except Exception as e:
        print(f"❌ 等待 back 信号出错: {e}")
        return False


# ============================================================
# 位置获取
# ============================================================

async def get_current_position():
    """
    获取机器人当前位置
    通过子进程调用 get_pose.py (使用系统 Python3.8)
    """
    command = (
        "source /opt/ros/foxy/setup.bash && "
        "timeout 3 python3 /home/unitree/unitree_sdk2_python/navi_update/get_pose.py simple 2>/dev/null | tail -1"
    )
    
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode().strip()
        
        if not output or output.startswith('#'):
            print(f"⚠️ 未能获取位置信息")
            return None
        
        parts = output.split()
        if len(parts) == 7:
            position = {
                'x': float(parts[0]),
                'y': float(parts[1]),
                'z': float(parts[2]),
                'qx': float(parts[3]),
                'qy': float(parts[4]),
                'qz': float(parts[5]),
                'qw': float(parts[6])
            }
            print(f"📍 当前位置: ({position['x']:.3f}, {position['y']:.3f})")
            return position
        else:
            print(f"⚠️ 位置数据格式错误: {output}")
            return None
            
    except Exception as e:
        print(f"❌ 获取位置失败: {e}")
        return None


async def save_departure_position():
    """保存出发位置"""
    global departure_position
    
    print("\n📍 记录出发位置...")
    departure_position = await get_current_position()
    
    if departure_position:
        print(f"✓ 出发位置已记录:")
        print(f"   坐标: ({departure_position['x']:.3f}, {departure_position['y']:.3f}, {departure_position['z']:.3f})")
        print(f"   姿态: ({departure_position['qx']:.3f}, {departure_position['qy']:.3f}, {departure_position['qz']:.3f}, {departure_position['qw']:.3f})")
    else:
        print("⚠️ 无法获取出发位置，将使用 '初始位置' 作为默认返回点")
    
    return departure_position


# ============================================================
# 导航控制
# ============================================================

async def execute_sub_task(sub_task):
    """执行单个子任务"""
    print(f"\n{'='*60}")
    print(f"🔧 执行子任务: {sub_task.task_type.value}")
    print(f"   数据: {sub_task.data}")
    print(f"{'='*60}\n")
    
    if sub_task.task_type == TaskType.NAVIGATE:
        location = sub_task.data["location"]
        purpose = sub_task.data.get("purpose", "导航")
        
        print(f"🚶 {purpose}: 前往 '{location}'")
        
        # 获取路径点列表
        if location == "__DEPARTURE__":
            departure_pos = sub_task.data.get("departure_position")
            if departure_pos:
                location_name = "出发点"
                print(f"📍 使用记录的出发位置: ({departure_pos['x']:.3f}, {departure_pos['y']:.3f})")
                poses_list = [(
                    departure_pos['x'], departure_pos['y'], departure_pos['z'],
                    departure_pos['qx'], departure_pos['qy'], departure_pos['qz'], departure_pos['qw']
                )]
            else:
                print("⚠️ 出发位置未记录，使用 '初始位置'")
                poses_list = location_poses_mapping.get("初始位置")
                location_name = "初始位置"
        elif location in location_poses_mapping:
            poses_list = location_poses_mapping[location]
            location_name = location
        else:
            print(f"⚠️ 警告: 未配置地点 '{location}' 的路径点")
            return
        
        # 发送导航目标
        await send_nav_goal(poses_list, location_name)
        
        # 如果有暂停的任务，恢复导航
        if len(task_manager.paused_tasks) > 0:
            print("⏯️  检测到中断任务，发送 resume 确保恢复")
            await asyncio.sleep(0.5)
            await send_resume()
        
        print(f"✓ 导航目标已发送")


async def send_nav_goal(poses_list, location_name=""):
    """发送导航目标"""
    print(f"\n🎯 发送导航目标: {location_name}")
    print(f"   路径点数量: {len(poses_list)}")
    
    for i, pose in enumerate(poses_list):
        print(f"   点 {i+1}: ({pose[0]:.3f}, {pose[1]:.3f})")
    
    try:
        nav.start_async(poses_list, speed=0.5)
        print(f"✓ 导航到 {location_name} 已启动")
    except Exception as e:
        print(f"❌ 导航启动失败: {e}")
        import traceback
        traceback.print_exc()
    
    await asyncio.sleep(0.5)


async def send_resume():
    """恢复导航"""
    try:
        nav.resume()
        print("✓ 导航已恢复")
    except Exception as e:
        print(f"❌ 恢复导航失败: {e}")


async def send_pause():
    """暂停导航"""
    try:
        nav.pause()
        print("⏸️  导航已暂停")
    except Exception as e:
        print(f"❌ 暂停导航失败: {e}")


# ============================================================
# 任务处理
# ============================================================

async def process_task(item, locations, delivery_location=None):
    """处理新任务：添加到任务管理器"""
    global departure_position
    
    if delivery_location is None:
        print("\n📍 未指定送达地点，记录当前位置作为返回点...")
        await save_departure_position()
    
    task_id = task_manager.add_task(item, locations, delivery_location, departure_position)
    
    await execute_tasks()


async def process_interrupt_task(item, locations, delivery_location=None):
    """处理中断任务：暂停当前任务，执行紧急任务"""
    global departure_position
    
    print("⏸️  暂停当前导航...")
    await send_pause()
    await asyncio.sleep(0.5)
    
    if delivery_location is None:
        print("\n📍 未指定送达地点，记录当前位置作为返回点...")
        await save_departure_position()
    
    task_id = task_manager.interrupt_and_execute(item, locations, delivery_location, departure_position)
    
    await execute_tasks()


async def execute_tasks():
    """执行任务循环"""
    while True:
        sub_task = task_manager.get_next_sub_task()
        
        if sub_task is None:
            print("\n✅ 任务队列为空")
            break
        
        await execute_sub_task(sub_task)
        
        if sub_task.task_type == TaskType.NAVIGATE:
            break  # 退出循环，等待 arrived 信号


# ============================================================
# WebSocket 监听主循环
# ============================================================

async def listen():
    """连接到服务器并监听消息"""
    uri = "ws://172.50.0.211:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ 已连接到服务器 ({uri})")
            print("等待接收消息...\n")

            while True:
                try:
                    message = await websocket.recv()
                    print(f"\n📨 收到消息: {message}")
                    
                    try:
                        data = json.loads(message)
                        
                        if "item" in data and "locations" in data:
                            item = data["item"]
                            locations = data["locations"]
                            delivery_location = data.get("delivery_location")
                            
                            print(f"🎯 识别结果:")
                            print(f"   物品: {item}")
                            print(f"   地点: {locations}")
                            if delivery_location:
                                print(f"   送达地点: {delivery_location} ⭐")
                            
                            is_interrupt = task_manager.current_task is not None
                            
                            if is_interrupt:
                                print("🚨 检测到新任务，中断当前任务")
                                await process_interrupt_task(item, locations, delivery_location)
                            else:
                                await process_task(item, locations, delivery_location)
                    
                    except json.JSONDecodeError:
                        # ===== 处理 arrived 消息 =====
                        if message == "arrived":
                            print("\n✅ 机器人已到达导航目标")
                            
                            current_sub = task_manager.execution_stack[-1] if task_manager.execution_stack else None
                            
                            if current_sub and current_sub.task_type == TaskType.NAVIGATE:
                                purpose = current_sub.data.get("purpose")
                                
                                # 获取 item 信息
                                item = current_sub.data.get("item")
                                if not item:
                                    main_task = task_manager.current_task
                                    if main_task:
                                        item = main_task.item
                                
                                # 获取位置名称
                                location_name = current_sub.data.get("location", "")
                                
                                # ===== 情况1：到达取物品位置 =====
                                if purpose == "取物品":
                                    print("📍 到达取物品位置")
                                    
                                    obj_name = current_sub.data.get("obj_name", "")
                                    
                                    if item and obj_name:
                                        # 👇 执行完整抓取流程：蹲下 -> 发送目标 -> 等待back -> 站起来
                                        await execute_grasp_sequence(
                                            item, obj_name, location_name, websocket
                                        )
                                    else:
                                        print(f"⚠️ 缺少抓取信息: item={item}, obj_name={obj_name}")
                                    
                                    # 完成当前子任务，继续下一个
                                    task_manager.complete_current_sub_task()
                                    await execute_tasks()
                                
                                # ===== 情况2：到达送物品位置 =====
                                elif purpose == "送物品":
                                    print("📍 到达送物品位置")
                                    
                                    if item and item in item_mapping:
                                        audio_file = item_mapping[item]["complete_audio"]
                                        try:
                                            print(f"🔊 播放完成音效: {os.path.basename(audio_file)}")
                                            threading.Thread(target=play_audio, args=(audio_file,), daemon=True).start()
                                            await asyncio.sleep(5)
                                        except Exception as e:
                                            print(f"❌ 播放音效失败: {e}")
                                    
                                    print("⏳ 等待用户取走物品...")
                                    await asyncio.sleep(3)
                                    print("✓ 继续执行下一个任务")
                                    
                                    task_manager.complete_current_sub_task()
                                    await execute_tasks()
                                
                                # ===== 情况3：到达返回位置 =====
                                elif purpose == "返回":
                                    print("📍 到达返回位置")
                                    
                                    if item and item in item_mapping:
                                        audio_file = item_mapping[item]["complete_audio"]
                                        try:
                                            print(f"🔊 播放完成音效: {os.path.basename(audio_file)}")
                                            threading.Thread(target=play_audio, args=(audio_file,), daemon=True).start()
                                            await asyncio.sleep(3)
                                        except Exception as e:
                                            print(f"❌ 播放音效失败: {e}")
                                    
                                    print("⏳ 等待用户取走物品...")
                                    await asyncio.sleep(3)
                                    print("✓ 任务完成")
                                    
                                    task_manager.complete_current_sub_task()
                                    await execute_tasks()
                                
                                # ===== 情况4：中转位置 =====
                                else:
                                    print(f"📍 到达 {purpose} 位置")
                                    task_manager.complete_current_sub_task()
                                    await execute_tasks()
                            else:
                                print("⚠️ 警告: 收到 arrived 但没有正在执行的导航任务")
                        
                        # ===== 处理 back 消息（在非抓取流程中收到的 back）=====
                        elif message == "back":
                            print("\n⚠️ 收到意外的 'back' 信号（不在抓取流程中），已忽略")
                        elif message == "pause":
                            print("\n⏸️  收到 'pause' 信号（唤醒词触发）")
                            await send_pause()
                
                except websockets.exceptions.ConnectionClosed:
                    print("❌ 连接已关闭")
                    break
                except Exception as e:
                    print(f"❌ 接收消息出错: {e}")
                    import traceback
                    traceback.print_exc()
                    break

    except Exception as e:
        print(f"❌ 连接失败: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 语音识别客户端 - 导航控制 (AsyncNavigationManager)")
    print("="*60)
    print("\n📌 功能:")
    print("   接收物品和地点信息")
    print("   自动规划导航路径")
    print("   到达后自动执行：蹲下 -> 抓取 -> 站起")
    print("   使用 AsyncNavigationManager API 控制机器人")
    print("\n📦 支持的物品:")
    for item, config in item_mapping.items():
        print(f"   - {item} ({config['obj_name']})")
    print("\n📍 支持的地点:")
    for location in location_poses_mapping.keys():
        print(f"   - {location}")
    print("="*60 + "\n")
    
    asyncio.run(listen())