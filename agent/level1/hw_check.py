#!/usr/bin/env python3
import subprocess
import json
import re

def run_command(cmd):
    """执行 Shell 命令并返回输出字符串"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
        return result.stdout
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return str(e)

def check_usb_device(vid_pid, name, dev_type):
    """通过 lsusb 检查 USB 设备是否存在"""
    lsusb_out = run_command("lsusb")
    if vid_pid in lsusb_out or vid_pid.lower() in lsusb_out:
        return {"name": name, "type": dev_type, "interface": "USB", "status": "Online", "id": vid_pid}
    return {"name": name, "type": dev_type, "interface": "USB", "status": "Offline", "id": vid_pid}

def check_network_device(ip, name, dev_type):
    """通过 Ping 的系统状态码检查网络设备是否在线，完美兼容中英文系统"""
    try:
        # -c 1 发送1个包，-W 1 等待1秒超时
        # subprocess.run 会返回一个 CompletedProcess 对象，包含 returncode
        result = subprocess.run(f"ping -c 1 -W 1 {ip}", shell=True, capture_output=True, timeout=2)
        
        # returncode 为 0 代表命令执行成功（即 Ping 通了）
        if result.returncode == 0:
            return {"name": name, "type": dev_type, "interface": f"Ethernet ({ip})", "status": "Online"}
        else:
            return {"name": name, "type": dev_type, "interface": f"Ethernet ({ip})", "status": "Offline"}
    except Exception as e:
        return {"name": name, "type": dev_type, "interface": f"Ethernet ({ip})", "status": "Error"}

def check_audio_device(keyword, name, dev_type):
    """通过 arecord 检查音频输入设备"""
    arecord_out = run_command("arecord -l")
    if keyword in arecord_out:
        return {"name": name, "type": dev_type, "interface": "USB Audio", "status": "Online"}
    return {"name": name, "type": dev_type, "interface": "USB Audio", "status": "Offline"}

def run_post_check():
    print("🚀 正在执行硬件上电自检 (POST)...\n")
    
    config = {
        "system": "Unitree Go2 Edu - Jetson Host",
        "post_result": "PASS",
        "hardware_list": []
    }

    # 1. 检测 RealSense D435i (Intel VID: 8086, PID: 0b3a)
    d435i_status = check_usb_device("8086:0b3a", "RealSense D435i", "RGB-D Camera")
    config["hardware_list"].append(d435i_status)

    # 2. 检测 Livox MID360 激光雷达 / 前置相机
    mid360_ip = "192.168.123.20" 
    mid360_status = check_network_device(mid360_ip, "Livox MID360", "3D LiDAR")
    config["hardware_list"].append(mid360_status)

    # 3. 检测 宇树底层运动控制板 (CM4)
    # 宇树默认内部通信网段通常为 192.168.123.x
    cm4_status = check_network_device("192.168.123.161", "Unitree CM4 Base", "Robot Controller")
    config["hardware_list"].append(cm4_status)

    # 4. 检测 外接麦克风设备 (如 DJI Mic)
    mic_status = check_audio_device("DJI MIC", "DJI Mic Mini", "Microphone")
    config["hardware_list"].append(mic_status)

    # 综合评估
    offline_count = sum(1 for dev in config["hardware_list"] if dev["status"] == "Offline")
    if offline_count > 0:
        config["post_result"] = f"WARNING: {offline_count} device(s) offline"

    return config

if __name__ == "__main__":
    hw_config = run_post_check()
    
    # 打印格式化后的 JSON 结果
    print(json.dumps(hw_config, indent=4, ensure_ascii=False))
    
    # 可选：将结果保存到文件中供后续脚本读取
    with open("/home/unitree/unitree_sdk2_python/agent/level1/hw_config.json", "w") as f:
        json.dump(hw_config, f, indent=4, ensure_ascii=False)
    print("\n✅ 配置已保存至 /home/unitree/unitree_sdk2_python/agent/level1/hw_config.json")