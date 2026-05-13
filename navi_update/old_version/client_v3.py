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

from task_manager_v3 import TaskManager, TaskType
from unitree_nav import AsyncNavigationManager
# 👇 引入 TTS 模块并初始化
from tts import speak_with_cherry, init_dashscope_api_key
init_dashscope_api_key()


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

import time
ignore_arrived_until = 0.0


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
# 位置获取
# ============================================================

# ...existing code...
async def get_current_position():
    """
    获取机器人当前位置
    通过子进程调用 get_pose.py (使用系统 Python3.8, 避免 Conda 环境冲突)
    """
    # 👇 修改关键点：明确指定使用 /usr/bin/python3，并确保环境变量干净
    command = (
        "export PYTHONPATH=/opt/ros/foxy/lib/python3.8/site-packages && "
        "source /opt/ros/foxy/setup.bash && "
        "timeout 5 /usr/bin/python3 /home/unitree/unitree_sdk2_python/navi_update/get_pose.py simple 2>/dev/null | tail -1"
    )
    
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # 👇 关键：如果不希望继承当前conda环境，可以考虑传 env=None 或手动净化 PATH，
            # 但通常上面的 explicit python path 加上 source setup.bash 足够了。
            # 如果还不行，可以在这里重置部分环境变量
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode().strip()
        
        if not output or output.startswith('#'):
            print(f"⚠️ 未能获取位置信息")
            # 打印错误用于调试
            if stderr:
                print(f"⚠️ 调试错误信息: {stderr.decode().strip()}")
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
# ...existing code...


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
    """
    负责具体执行动作。
    ⚠️ 绝对不要在这里面调用 await execute_tasks() 造成地狱递归！
    """
    task_type = sub_task.task_type
    data = sub_task.data
    
    print(f"\n⚡ 注入动作: [{task_type.value.upper()}] data={data}")
    
    if task_type == TaskType.NAVIGATE:
        location = data["location"]
        if location == "__DEPARTURE__":
            departure_pos = data.get("departure_position")
            if departure_pos:
                poses_list = [(departure_pos['x'], departure_pos['y'], departure_pos['z'],
                               departure_pos['qx'], departure_pos['qy'], departure_pos['qz'], departure_pos['qw'])]
            else:
                poses_list = location_poses_mapping.get("初始位置")
        elif location in location_poses_mapping:
            poses_list = location_poses_mapping[location]
        else:
            print(f"⚠️ 警告: 无法识别导航点 {location}")
            return
            
        await send_nav_goal(poses_list, location)
        # 阻塞型操作，不标记 complete，引擎层会把控制权交还给 websocket
        
    elif task_type == TaskType.SQUAT:
        await execute_down_script(data.get("location", ""))
        await asyncio.sleep(1) # 姿态缓冲
        task_manager.complete_current_sub_task()
        
    elif task_type == TaskType.SEND_GRASP_MSG:
        item = data.get("item", "")
        obj_name = item_mapping.get(item, {}).get("obj_name", "unknown")
        await send_grasp_target(obj_name)
        task_manager.complete_current_sub_task()
        
    elif task_type == TaskType.WAIT_FOR_BACK:
        print("⏳ 触发挂起：等待机械臂 'back' 信号的异步回传...")
        
    elif task_type == TaskType.STAND_UP:
        await execute_up_script()
        await asyncio.sleep(2)
        task_manager.complete_current_sub_task()
        
    elif task_type == TaskType.PLAY_AUDIO:
        item = task_manager.current_task.item if task_manager.current_task else "物品"
        text_to_speak = f"您好，这是您需要的{item}，请取走。"
        threading.Thread(target=speak_with_cherry, args=(text_to_speak,), daemon=True).start()
        
        print("⏳ 物品已送达目的地，停留 7 秒等待取走...")
        await asyncio.sleep(7)
        task_manager.complete_current_sub_task()


async def execute_tasks():
    """提栈器引擎: 扁平化循环，彻底杜绝调用分身带来的混乱并发"""
    while True:
        sub_task = task_manager.get_next_sub_task()
        if sub_task is None:
            break
            
        await execute_sub_task(sub_task)
        
        # 只要经过执行依然没有被标记成 COMPLETED 状态的
        # 就说明这是一个（导航/等待机械臂）需要外部信号驱动的阻塞事务
        # 直接打断本层执行机的推进，交给 Listen 继续倾听，避免死循环！
        from task_manager_v3 import TaskStatus
        if sub_task.status != TaskStatus.COMPLETED:
            break


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
# WebSocket 监听主循环
# ============================================================

async def listen():
    """核心事件事件循环机"""
    global ignore_arrived_until
    uri = "ws://172.50.0.211:8765"
    async with websockets.connect(uri) as websocket:
        print(f"✅ 已连接核心总线")
        while True:
            try:
                message = await websocket.recv()
                print(f"\n📨 总线消息: {message}")
                
                try:
                    data = json.loads(message)
                    if "action_plan" in data:
                        # 记录全局原点
                        await save_departure_position()
                        
                        is_interrupt = task_manager.current_task is not None
                        if is_interrupt:
                            print("🚨 覆盖指令触发")
                            await send_pause()
                            
                            # 👇 1. 撑起 3 秒无敌护盾，此期间所有的 arrived 均为底板阵亡抛出的废弃物
                            ignore_arrived_until = time.time() + 3.0
                            task_manager.interrupt_and_execute(data["item"], data["action_plan"], departure_position)
                            
                            print("⏳ 强制排空底盘进程中，安全等待底盘恢复(3秒)...")
                            # 👇 2. 不卡死协程的延时触发
                            async def delayed_start():
                                await asyncio.sleep(3.0)
                                print("\n▶️ 底盘就绪，正式启动新导航目标！")
                                await execute_tasks()
                            
                            asyncio.create_task(delayed_start())
                        else:
                            task_manager.add_task(data["item"], data["action_plan"], departure_position)
                            await execute_tasks()
                
                except json.JSONDecodeError:
                    current_task = task_manager.execution_stack[-1] if task_manager.execution_stack else None
                    
                    if message == "arrived":
                        # 👇 3. 护盾起效验证
                        if time.time() < ignore_arrived_until:
                            print("🛡️ 护盾抵挡：已丢弃前一个意外终止任务产生的废弃 arrived")
                            continue
                            
                        if current_task and current_task.task_type == TaskType.NAVIGATE:
                            print("🛰️ [系统回调] 抵达真·导航点目标。驱动下一步")
                            task_manager.complete_current_sub_task()
                            await execute_tasks()
                            
                    elif message == "back":
                        if current_task and current_task.task_type == TaskType.WAIT_FOR_BACK:
                            print("🦾 [系统回调] 检测到抓取完成。驱动下一步")
                            task_manager.complete_current_sub_task()
                            await execute_tasks()
                        else:
                            print("⚠️ 忽略游离区外的 back 数据")

                    elif message == "pause":
                        is_interrupt = task_manager.current_task is not None
                        if is_interrupt:
                            ignore_arrived_until = time.time() + 3.0
                        await send_pause()

            except Exception as e:
                print(f"❌ 瘫痪报错: {e}")
                break


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