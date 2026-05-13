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
sys.path.insert(0, '/home/unitree/dky/go2_python_sdk2')
from play_audio import play_audio
import threading

from task_manager import TaskManager, TaskType

# 禁用代理（适用于本地连接，避免 SOCKS 代理问题）
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['socks_proxy'] = ''

# 物品到对象名称和音频文件的映射
item_mapping = {
    "水": {
        "obj_name": "bottle",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/water_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/water_start.wav"
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
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/umbrella_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/umbrella_start.wav"
    },
    "咖啡": {
        "obj_name": "brown bottle",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/coffee_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/coffee_start.wav"},
    "外卖": {
        "obj_name": "brown bag",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/takeout_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/takeout_start.wav"},
    "饮料": {
        "obj_name": "bottle",
        "complete_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/yinliao_complete.wav",
        "start_audio": "/home/unitree/dky/go2_python_sdk2/data/wav_files/yinliao_start.wav"}
}

# 地点到导航坐标的映射
location_mapping = {
    "前台": {
        "x": 19.982,
        "y": 17.929,
        "z": 0.048,
        "qx": -0.055,
        "qy": 0.018,
        "qz": -0.002,
        "qw": 0.998
    },

    "办公室": {
        "x": -1.249,
        "y": 1.971,
        "z": -0.020,
        "qx": -0.017,
        "qy": 0.047,
        "qz": 0.747,
        "qw": 0.663
    },
    "吧台": {
        "x": 0.983,
        "y": -2.088,
        "z": -0.003,
        "qx": 0.005,
        "qy": 0.027,
        "qz": -0.718,
        "qw": 0.696
    },
    "初始位置": {
        "x": -0.334,
        "y": -0.086,
        "z": -0.044,
        "qx": 0.018,
        "qy": 0.035,
        "qz": 0.012,
        "qw": 0.999
    },
    "门口": {
        "x": 7.931,
        "y": 16.522,
        "z": -0.005,
        "qx": -0.019,
        "qy": 0.017,
        "qz": 0.999,
        "qw": -0.052
    },
    "雨伞架":{
        "x": 6.040,
        "y": 3.369,
        "z": 0.028,
        "qx": -0.004,
        "qy": 0.022,
        "qz": 0.701,
        "qw": 0.713
    }
}

# 全局变量：存储当前任务的地点列表
current_locations = []
# 全局任务管理器
task_manager = TaskManager()
# current_audio_file = None


async def execute_sub_task(sub_task):
    """执行单个子任务"""
    global current_audio_file
    
    print(f"\n{'='*60}")
    print(f"🔧 执行子任务: {sub_task.task_type.value}")
    print(f"   数据: {sub_task.data}")
    print(f"{'='*60}\n")
    
    if sub_task.task_type == TaskType.NAVIGATE:
        # 导航任务
        location = sub_task.data["location"]
        purpose = sub_task.data.get("purpose", "导航")
        
        print(f"🚶 {purpose}: 前往 '{location}'")
        
        if location in location_mapping:
            # 检查是否需要抓取（第一个导航任务）
            if purpose == "取物品" and "obj_name" in sub_task.data:
                obj_name = sub_task.data["obj_name"]
                item = sub_task.data["item"]
                
                print(f"📦 此次导航将抓取: {item} ({obj_name})")
                
                # 提前发送 obj_name
                await send_obj_name(obj_name)
            
            
            # 发送导航目标
            await send_nav_goal(location_mapping[location], location)
            # 👇 新增：如果有暂停的任务，说明是中断任务，需要发送 resume
            if len(task_manager.paused_tasks) > 0:
                print("⏯️  检测到中断任务，发送 resume 确保恢复")
                await asyncio.sleep(0.5)
                await send_resume()
            
            print(f"✓ 导航目标已发送")
        
        else:
            print(f"⚠️ 警告: 未配置地点 '{location}' 的坐标")
    
    # elif sub_task.task_type == TaskType.GRASP:
    #     # ❌ 这个分支不再需要，因为没有 GRASP 任务了
    #     print(f"⚠️ 警告: 不应该有独立的 GRASP 任务")
        
async def send_nav_goal(goal_config, location_name=""):
    """发送导航目标"""
    print(f"\n🎯 发送导航目标: {location_name}")
    print(f"   坐标: ({goal_config['x']:.3f}, {goal_config['y']:.3f})")
    
    command = (
        "source /opt/ros/noetic/setup.bash && "
        "rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped "
        f"'{{header: {{frame_id: \"map\"}}, "
        f"pose: {{position: {{x: {goal_config['x']}, y: {goal_config['y']}, z: {goal_config['z']}}}, "
        f"orientation: {{x: {goal_config['qx']}, y: {goal_config['qy']}, z: {goal_config['qz']}, w: {goal_config['qw']}}}}}}}' "
        "-1"
    )
    
    process = await asyncio.create_subprocess_shell(
        command,
        executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if stdout:
        print(f"   rostopic pub 输出: {stdout.decode()}")
    if stderr and "WARNING" not in stderr.decode():  # 忽略警告
        print(f"   rostopic pub 错误: {stderr.decode()}")
    
    print(f"✓ 导航目标已发送")


async def send_resume():
    """发送恢复运动命令"""
    command = (
        "source /opt/ros/noetic/setup.bash && "
        'rostopic pub /neupan/resume std_msgs/Empty "{}" -1'
    )
    
    process = await asyncio.create_subprocess_shell(
        command,
        executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if stdout:
        print(f"rostopic pub 输出: {stdout.decode()}")
    if stderr:
        print(f"rostopic pub 错误: {stderr.decode()}")
    
    print("✓ 取消暂停")


async def send_obj_name(obj_name):
    """发送物体名称"""
    command = (
        f'source /opt/ros/noetic/setup.bash && '
        f'rostopic pub /obj_name std_msgs/String \'{{data: "{obj_name}"}}\' -1'
    )
    
    process = await asyncio.create_subprocess_shell(
        command,
        executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if stdout:
        print(f"rostopic pub 输出: {stdout.decode()}")
    if stderr:
        print(f"rostopic pub 错误: {stderr.decode()}")
    
    print(f"✓ 对象名称发送完成: {obj_name}")


async def send_back_signal():
    """发送back信号给neupan，表示抓取完成"""
    command = (
        "source /opt/ros/noetic/setup.bash && "
        'rostopic pub /back_signal std_msgs/Empty "{}" -1'
    )
    
    process = await asyncio.create_subprocess_shell(
        command,
        executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if stdout:
        print(f"rostopic pub 输出: {stdout.decode()}")
    if stderr:
        print(f"rostopic pub 错误: {stderr.decode()}")
    
    print("✓ back信号发送完成")


async def process_task(item, locations, delivery_location=None):
    """处理新任务：添加到任务管理器"""
    task_id = task_manager.add_task(item, locations, delivery_location)
    
    # 开始执行任务
    await execute_tasks()
    
async def process_interrupt_task(item, locations, delivery_location=None):
    """处理中断任务：暂停当前任务，执行紧急任务"""
    task_id = task_manager.interrupt_and_execute(item, locations, delivery_location)
    
    # 开始执行任务
    await execute_tasks()

async def execute_tasks():
    """执行任务循环"""
    while True:
        sub_task = task_manager.get_next_sub_task()
        
        if sub_task is None:
            print("\n✅ 任务队列为空")
            break
        
        # 执行子任务
        await execute_sub_task(sub_task)
        
        # 如果是导航任务，等待到达（实际应监听 ROS 话题）
        if sub_task.task_type == TaskType.NAVIGATE:
            # # TODO: 监听 /neupan/arrive 话题，而不是固定等待
            # await asyncio.sleep(5)  # 模拟等待到达
            # task_manager.complete_current_sub_task()
            break  # 退出循环，等待到达信号
        
        # 如果是抓取任务，等待 back 信号（在 handle_back_message 中完成）
        elif sub_task.task_type == TaskType.GRASP:
            # 由 handle_back_message 调用 complete_current_sub_task()
            break  # 退出循环，等待 back 信号

async def handle_back_message():
    """处理机械臂发送的back消息"""
    print(f"\n{'='*60}")
    print(f"🔙 收到机械臂 'back' 信号")
    print(f"{'='*60}\n")
    
    # 检查当前子任务类型
    current_sub = task_manager.execution_stack[-1] if task_manager.execution_stack else None
    
    if current_sub is None:
        print("⚠️ 警告: 没有正在执行的任务，忽略 back 信号")
        return
    
    # 只有当前任务是 GRASP 时才处理
    if current_sub.task_type == TaskType.GRASP:
        print(f"✓ 当前任务: {current_sub.task_type.value} - {current_sub.data}")
        print("📦 抓取完成，准备站起来")
        
        # 标记抓取任务完成
        task_manager.complete_current_sub_task()
        
        # 发送back信号给neupan，让机器人站起来
        print("📤 发送 /back_signal 给 neupan...")
        await send_back_signal()
        
        # 等待站起来完成
        print("⏳ 等待机器人站起来...")
        await asyncio.sleep(5)
        
        # 继续执行后续任务
        await execute_tasks()
    
    else:
        print(f"⚠️ 警告: 当前任务是 {current_sub.task_type.value}，不是 GRASP")
        print(f"   忽略 back 信号")


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
                                
                                # ===== 情况1：取物品位置（需要等待抓取） =====
                                if purpose == "取物品":
                                    print("📍 到达取物品位置")
                                    print("⏳ 等待机械臂抓取完成（'back' 信号）...")
                                    # 不做任何操作，等待 back 信号
                                
                                # ===== 情况2：送物品位置 =====
                                elif purpose == "送物品":
                                    item = current_sub.data.get("item")
                                    if not item:
                                        main_task = task_manager.current_task
                                        if main_task:
                                            item = main_task.item
                                    
                                    if item and item in item_mapping:
                                        audio_file = item_mapping[item]["complete_audio"]
                                        try:
                                            print(f"🔊 播放完成音效: {os.path.basename(audio_file)}")
                                            threading.Thread(target=play_audio, args=(audio_file,), daemon=True).start()
                                            await asyncio.sleep(5)
                                        except Exception as e:
                                            print(f"❌ 播放音效失败: {e}")
                                    # 👇 新增：等待用户取走物品
                                    print("⏳ 等待用户取走物品...")
                                    await asyncio.sleep(3)  # 👈 等待 5 秒
                                    print("✓ 继续执行下一个任务")
                                    task_manager.complete_current_sub_task()
                                    await execute_tasks()
                                
                                # ===== 情况3：中转/返回 =====
                                else:
                                    print(f"📍 到达 {purpose} 位置")
                                    task_manager.complete_current_sub_task()
                                    await execute_tasks()
                            else:
                                print("⚠️ 警告: 收到 arrived 但没有正在执行的导航任务")
                        
                        # ===== 处理 back 消息 =====
                        elif message == "back":
                            print("\n✅ 收到 'back' 信号：机械臂抓取完成")
                            
                            current_sub = task_manager.execution_stack[-1] if task_manager.execution_stack else None
                            
                            if current_sub and current_sub.task_type == TaskType.NAVIGATE:
                                if current_sub.data.get("purpose") == "取物品":
                                    print("📦 抓取流程完成，准备站起来")
                                    
                                    print("📤 发送 /back_signal 给 neupan...")
                                    await send_back_signal()
                                    
                                    print("⏳ 等待机器人站起来...")
                                    await asyncio.sleep(5)
                                    
                                    # 完成当前子任务
                                    task_manager.complete_current_sub_task()
                                    
                                    # 继续执行后续任务
                                    await execute_tasks()
                                else:
                                    print(f"⚠️ 警告: 收到 back 但当前任务 purpose 不是 '取物品'")
                                    print(f"   当前 purpose: {current_sub.data.get('purpose')}")
                            else:
                                print("⚠️ 警告: 收到 back 但没有正在执行的任务")
                
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
    print("🤖 语音识别客户端 - 导航控制")
    print("="*60)
    print("\n📌 功能:")
    print("   接收物品和地点信息")
    print("   自动规划导航路径")
    print("   控制机器人执行任务")
    print("\n📦 支持的物品:")
    for item, config in item_mapping.items():
        print(f"   - {item} ({config['obj_name']})")
    print("\n📍 支持的地点:")
    for location in location_mapping.keys():
        print(f"   - {location}")
    print("="*60 + "\n")
    
    asyncio.run(listen())