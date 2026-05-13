# -*- coding: utf-8 -*-
"""
实时语音识别 - Client 接收端
需要安装: pip install websockets
使用方式: python client.py
连接到服务器并接收消息
"""

import os
import sys
import re
import json
import time
import cv2
import base64
import logging
import asyncio
import websockets
import subprocess
import threading

sys.path.insert(0, '/home/unitree/dky/go2_python_sdk2')
sys.path.insert(0, '/home/unitree/unitree_go2')

from play_audio import play_audio
from task_manager_recon_v3 import TaskManager, TaskType,TaskStatus
from unitree_nav import AsyncNavigationManager
from tts_v8 import speak_with_cherry, init_dashscope_api_key
from agent.level2.mp_single_realsense import RealSenseSubProcess
init_dashscope_api_key()

# ===== 全局配置 -*-
WEBSOCKET_URI = "ws://172.50.1.8:8765"  # 连接机器狗8765端口

# 禁用代理（适用于本地连接，避免 SOCKS 代理问题）
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['socks_proxy'] = ''

nav = AsyncNavigationManager() # 全局导航对象
task_manager = TaskManager() # 全局任务管理器
cam = RealSenseSubProcess(fps=15) # 全局相机实例 子进程初始化

global_websocket = None # 全局 websocket 引用（用于接收 back 消息）
departure_position = None # 全局变量：存储出发位置
ignore_arrived_until = 0.0

# 物品到对象名称和音频文件的映射
item_mapping = {
    "纸": {
        "obj_name": "tissue",
    },
    "外卖": {
        "obj_name": "brown bag",
    },
    "可乐": {
        "obj_name": "coke",
    },
    "芬达": {
        "obj_name": "juice",
    },
    "椰子水": {
        "obj_name": "white bottle",
    },
}

# 地点到导航路径点列表的映射
location_poses_mapping = {
    "前台": [
        (2.98671, -0.307209, 0.067685, 0.0051042, -0.121825, -0.0396321, -0.991747),
        # (4.96802, -0.0545474, 0.0722993, -0.0970867, 0.105798, 0.706048, 0.693454),
    ],
    "办公室": [
        # (0.00240726, -0.514558, 0.0382567, 0.0061988, -0.137903, -0.00690807, 0.990402),
        # (-1.03291, 2.10079, 0.0331177, 0.111722 , -0.0748998 , -0.851018, -0.507618)
        (-0.228292, -2.92795, 0.0324798, 0.0927021, 0.00835202, -0.983461, -0.155372)
    ],
    "吧台": [
        # (-1.30207, -1.06263, 0.0280621 , 0.116096 , 0.0217395, -0.993, -0.000853713),
        # (-3.28101,-0.938665,0.0165448,0.100462,0.0467847,-0.99378 ,0.0109221)
        (2.59608, -1.00364, 0.0356971, 0.0138585, 0.0955315, -0.200003, 0.975028),
        (4.4825, -2.08375, 0.0251833, 0.00932857, 0.115608, -0.117356, 0.986294)
    ],

    "起点": [
        # (-0.467805 , -1.00111,0.0201036,-0.0410159, 0.129722,0.188151, 0.972671),
        # (0.0907377,1.18321,0.0225484,-0.101463,0.0806533 ,0.678303,0.723261)
        (-0.239543, 0.0142876, 0.043754, -0.00813959, 0.0897152, 0.0824621, 0.992514)
    ],
    "门口": [
        (7.931, 16.522, -0.005, -0.019, 0.017, 0.999, -0.052)
    ],
    "巡检点1": [  
    ],
    "巡检点2": [ 
    ],
}


# ============================================================
# 位置获取
# ============================================================

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
        )
        stdout, stderr = await process.communicate()

        output = stdout.decode().strip()

        if not output or output.startswith('#'):
            print(f"⚠️ 未能获取位置信息")
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
# 机器人动作控制函数（从 neupan 迁移过来）
# ============================================================

# 机械臂控制，操作阶段提示发布，不涉及具体的目标与位姿
async def send_grasp_target(obj_name):
    """
    发送抓取目标给机械臂
    通过 ROS2 话题 /grasp_target 发送
    """
    command = (
        "source /opt/ros/noetic/setup.bash && "
        f'rostopic pub -1 /grasp_target std_msgs/String "{{data: \'{obj_name}\'}}" --once'
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

async def send_release_target():
    """
    发送放下目标给机械臂
    通过 ROS2 话题 /grasp_target 发送 'put' 信号
    """
    command = (
        "source /opt/ros/noetic/setup.bash && "
        f'rostopic pub -1 /grasp_target std_msgs/String "data: \'put\'" --once'
    )
    try:
        print(f"👐 开始向机械臂发送放下指示 (put)...")
        process = await asyncio.create_subprocess_shell(
            command,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await process.communicate()
        print(f"✓ 放下目标已发送")
    except Exception as e:
        print(f"❌ 发送放下目标失败: {e}")

# 机器狗本体控制
async def execute_down_script(location_name=""):
    """
    执行蹲下脚本
    根据位置选择不同的 down 脚本
    """
    if location_name == "门口":
        script_path = "/home/unitree/unitree_sdk2_python/navi_update/actions/stand_down.py"
        print(f"🚪 检测到位置：门口，执行 down_door.py")
    else:
        script_path = "/home/unitree/unitree_sdk2_python/navi_update/actions/stand_down.py"
        print(f"📍 当前位置：{location_name or '未知'}，执行 down.py")

    command = (
        "source ~/miniconda3/etc/profile.d/conda.sh && "
        "conda activate go2_navi && "
        "source /opt/ros/foxy/setup.bash && "
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
        "export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds && "
        "export PYTHONPATH=$PYTHONPATH:~/unitree_sdk2_python && "
        "python /home/unitree/unitree_sdk2_python/navi_update/actions/stand_up.py eth0"
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

async def execute_action_script(script_name, action_name_cn):
    """通用的高层脚本执行器，根据传入的 py 脚本名执行运动"""
    script_path = f"/home/unitree/unitree_sdk2_python/navi_update/actions/{script_name}"
    print(f"🤸 开始执行动作: {action_name_cn} -> {script_name}")
    command = (
        "source ~/miniconda3/etc/profile.d/conda.sh && "
        "conda activate go2_navi && "
        "source /opt/ros/foxy/setup.bash && "
        "export CYCLONEDDS_HOME=~/cyclonedds_ws/install/cyclonedds && "
        "export PYTHONPATH=$PYTHONPATH:~/unitree_sdk2_python && "
        f"python {script_path} eth0"
    )
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await process.communicate()
        if process.returncode == 0:
            print(f"✓ {action_name_cn} 动作完成")
        else:
            print(f"❌ {action_name_cn} 动作执行失败")
    except Exception as e:
        print(f"❌执行 {action_name_cn} 崩溃: {e}")

# ============================================================
# 导航控制
# ============================================================

# 基础导航函数
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
# 复合任务，巡检等
# ============================================================

# ============================================================
# 执行任务
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

    # ===== 以下为原地操作动作，不需要记录初始位置 =====
    elif task_type == TaskType.SQUAT:
        await execute_down_script(data.get("location", ""))
        await asyncio.sleep(1)
        task_manager.complete_current_sub_task()

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

    elif task_type == TaskType.HELLO:
        await execute_action_script("hello.py", "打招呼")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.ROTATE:
        await execute_action_script("rotate.py", "旋转")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.LIE_DOWN:
        await execute_action_script("stand_down.py", "趴下")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.STRETCH:
        await execute_action_script("stretch.py", "伸懒腰")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.WALK_FORWARD:
        await execute_action_script("walk_forward.py", "向前走")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.WALK_BACKWARD:
        await execute_action_script("walk_backward.py", "向后走")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.WALK_LEFT:
        await execute_action_script("walk_left.py", "向左移动")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.WALK_RIGHT:
        await execute_action_script("walk_right.py", "向右移动")
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.CAPTURE_PHOTO:
        print("📸 正在拍照...")
        rgbs, depths, info = cam.get_images(num_frames=1)
        if len(rgbs) > 0:
            # 编码为 JPEG base64
            _, jpeg_buf = cv2.imencode('.jpg', rgbs[-1], [cv2.IMWRITE_JPEG_QUALITY, 85])
            img_b64 = base64.b64encode(jpeg_buf).decode('utf-8')
            # 通过 websocket 发回 server
            if global_websocket:
                await global_websocket.send(json.dumps({
                    "type": "photo",
                    "data": img_b64,
                    "timestamp": time.time()
                }))
                print("✓ 照片已发送至服务端")
            else:
                print("⚠️ WebSocket 未连接，无法发送照片")
        else:
            print("⚠️ 相机无数据")
        task_manager.complete_current_sub_task()

    # 机械臂相关操作
    elif task_type == TaskType.SEND_GRASP_MSG:
        item = data.get("item", "")
        obj_name = item_mapping.get(item, {}).get("obj_name", "unknown")
        await send_grasp_target(obj_name)
        task_manager.complete_current_sub_task()

    elif task_type == TaskType.WAIT_FOR_BACK:
        print("⏳ 触发挂起：等待机械臂 'back' 信号的异步回传...")

    elif task_type == TaskType.RELEASE_ITEM:
        await send_release_target()
        task_manager.complete_current_sub_task()

async def execute_tasks():
    """提栈器引擎: 扁平化循环，彻底杜绝调用分身带来的混乱并发"""
    while True:
        sub_task = task_manager.get_next_sub_task()
        if sub_task is None:
            break

        await execute_sub_task(sub_task)

        if sub_task.status != TaskStatus.COMPLETED:
            break


# ============================================================
# WebSocket 监听主循环
# ============================================================

async def listen():
    """核心事件事件循环机"""
    global ignore_arrived_until, global_websocket

    # 启动相机子进程
    print("📷 正在初始化相机...")
    cam.start()
    print("✓ 相机已启动")

    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            global_websocket = websocket
            print(f"✅ 已连接核心总线")
            while True:
                try:
                    # 接受LLM生成的action plan
                    message = await websocket.recv()
                    print(f"\n📨 总线消息: {message}")

                    try:
                        data = json.loads(message)
                        # 这种情况有 动作发送过来，大概率是新任务，有可能当前没在执行动作，也可能正在执行，进入指令覆盖模式
                        if "action_plan" in data:
                            action_plan = data["action_plan"]

                            # 👇 1. 扫描判定: 是否为需要占用底盘雷达的"导航任务"
                            is_nav_task = any(step.get("action") == "navigate" for step in action_plan)

                            # 👇 2. 差异化: 只有导航任务才需要花时间记录原点坐标
                            if is_nav_task:
                                await save_departure_position()
                            else:
                                print("🎭 纯表演指示: 略过初始位置记录")

                            is_interrupt = task_manager.current_task is not None
                            if is_interrupt:
                                print("🚨 覆盖指令触发")
                                await send_pause()

                                ignore_arrived_until = time.time() + 3.0

                                # 压入新任务（如果是非导航任务，出发点设为None即可）
                                departure_arg = departure_position if is_nav_task else None
                                task_manager.interrupt_and_execute(data.get("item"), action_plan, departure_arg)

                                # 👇 3. 差异化: 纯体态表现直接瞬间提栈，导航才延时降温！
                                if is_nav_task:
                                    print("⏳ 强制排空底盘进程中，安全等待底盘恢复(3秒)...")
                                    async def delayed_start():
                                        await asyncio.sleep(3.0)
                                        print("\n▶️ 底盘就绪，正式启动新导航目标！")
                                        await execute_tasks()
                                    asyncio.create_task(delayed_start())
                                else:
                                    print("⚡ 纯体态动作响应：无需等待底盘冷却，瞬间切换动作！")
                                    await execute_tasks()
                            else:
                                departure_arg = departure_position if is_nav_task else None
                                task_manager.add_task(data.get("item"), action_plan, departure_arg)
                                await execute_tasks()

                    except json.JSONDecodeError:
                        # 这种情况服务器返回的是简单的标志符，需要调控后续执行什么动作
                        current_task = task_manager.execution_stack[-1] if task_manager.execution_stack else None

                        # 导航到对应位置会返回到达标识符
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

                        elif message == "play":
                            if current_task and current_task.task_type == TaskType.WAIT_FOR_PLAY:
                                print("🦾 [系统回调] 检测到彻底放下完成。准备驱动语音广播！")
                                task_manager.complete_current_sub_task()
                                await execute_tasks()
                            else:
                                print("⚠️ 忽略游离区外的 play 数据")

                        elif message == "pause":
                            is_interrupt = task_manager.current_task is not None
                            if is_interrupt:
                                ignore_arrived_until = time.time() + 3.0
                            await send_pause()

                except Exception as e:
                    print(f"❌ 瘫痪报错: {e}")
                    break
    finally:
        # 停止相机子进程
        print("📷 正在关闭相机...")
        cam.stop()
        print("✓ 相机已关闭")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 语音识别客户端 - 导航控制 (AsyncNavigationManager)")
    print("="*60)
    print("\n📌 功能:")
    print("   接收物品和地点信息")
    print("   自动规划导航路径")
    print("   到达后自动执行：蹲下 -> 抓取 -> 站起")
    print("   使用 AsyncNavigationManager API 控制机器人")
    print("   支持拍照功能，照片保存在服务端")
    print("\n📦 支持的物品:")
    for item, config in item_mapping.items():
        print(f"   - {item} ({config['obj_name']})")
    print("\n📍 支持的地点:")
    for location in location_poses_mapping.keys():
        print(f"   - {location}")
    print("="*60 + "\n")

    asyncio.run(listen())
