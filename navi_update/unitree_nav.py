import subprocess
import json
import tempfile
import os
import time
import websocket  # pip install websocket-client
from threading import Thread

class AsyncNavigationManager:
    def __init__(self, executable='/unitree/module/unitree_slam/example/build/simple_nav_v3'):
        self.executable = executable
        self.nav_process = None
        self._monitor_thread = None
        self.ws_uri = "ws://172.50.1.125:8765"  # 👈 新增
    
    def start_async(self, pose_list, speed=0.5, mode=0, loop_mode=0):
        """异步开始导航"""
        poses_json = {"poses": []}
        
        for pose in pose_list:
            if isinstance(pose, dict):
                poses_json["poses"].append(pose)
            else:
                poses_json["poses"].append({
                    "x": pose[0], "y": pose[1], "z": pose[2],
                    "q_x": pose[3], "q_y": pose[4], "q_z": pose[5], "q_w": pose[6]
                })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(poses_json, f)
            temp_file = f.name
        
        cmd = [self.executable, 'start', temp_file, str(speed), str(mode), str(loop_mode)]
        print(f"启动导航: {' '.join(cmd)}")
        
        self.nav_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"导航已启动 (PID: {self.nav_process.pid})")

        # 👇 新增：启动监控线程，导航完成后发送 arrived
        self._monitor_thread = Thread(target=self._monitor_and_notify, daemon=True)
        self._monitor_thread.start()

        return self.nav_process
    
    def _monitor_and_notify(self):
        """监控导航进程，完成后发送 arrived 消息"""
        if self.nav_process is None:
            return
        
        stdout, stderr = self.nav_process.communicate()
        ret = self.nav_process.returncode
        
        print(f"[导航进程] 已结束，返回码: {ret}")
        if stdout:
            print(f"[导航进程] stdout: {stdout.strip()}")
        
        if ret == 0:
            print("📡 导航完成，发送 arrived 消息...")
            self._send_arrived()
        else:
            print(f"❌ 导航失败 (returncode={ret})，不发送 arrived")
            if stderr:
                print(f"[导航进程] stderr: {stderr.strip()}")

    def _send_arrived(self):
        """通过 WebSocket 发送 arrived 消息"""
        try:
            ws = websocket.create_connection(self.ws_uri, timeout=5)
            ws.send("arrived")
            ws.close()
            print("✓ arrived 消息已发送")
        except Exception as e:
            print(f"❌ 发送 arrived 失败: {e}")

    # ...existing code...
    def pause(self):
        """暂停"""
        subprocess.run([self.executable, 'pause'])
    
    def resume(self):
        """恢复"""
        subprocess.run([self.executable, 'resume'])
    
    def stop(self):
        """停止"""
        subprocess.run([self.executable, 'stop'])
        if self.nav_process:
            self.nav_process.wait()
    
    def wait(self):
        """等待完成"""
        if self.nav_process:
            self.nav_process.wait()