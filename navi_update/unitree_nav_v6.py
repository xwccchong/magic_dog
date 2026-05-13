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
        self.ws_uri = "ws://172.50.1.125:8765"
        # 拍照相关
        self._cam = None

    def set_photo_handler(self, cam):
        """设置拍照所需的相机

        Args:
            cam: RealSense 相机实例
        """
        self._cam = cam

    def start_async(self, pose_list, speed=0.5, mode=0, loop_mode=0):
        """异步开始导航（一次性导航所有点）"""
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

        # 启动监控线程
        self._monitor_thread = Thread(target=self._monitor_and_notify, daemon=True)
        self._monitor_thread.start()

        return self.nav_process

    def start_async_with_photo(self, pose_list, speed=0.5, mode=0, loop_mode=0,
                                wait_stable_time=4.0, photo_on_arrival=True):
        """逐点导航，每到一个点后等待稳定并拍照

        Args:
            pose_list: 目标位姿列表
            speed: 导航速度
            mode: 导航模式
            loop_mode: 循环模式
            wait_stable_time: 到达后等待稳定的时间（秒）
            photo_on_arrival: 是否在到达后拍照
        """
        if not self._cam:
            print("⚠️ 未设置相机，将使用普通导航模式（无拍照）")
            return self.start_async(pose_list, speed, mode, loop_mode)

        # 启动逐点导航线程
        self._monitor_thread = Thread(
            target=self._navigate_point_by_point,
            args=(pose_list, speed, mode, loop_mode, wait_stable_time, photo_on_arrival),
            daemon=True
        )
        self._monitor_thread.start()

        return None

    def _navigate_point_by_point(self, pose_list, speed, mode, loop_mode,
                                  wait_stable_time, photo_on_arrival):
        """逐点导航的内部实现"""
        import cv2
        import base64
        import numpy as np

        total_poses = len(pose_list)
        print(f"🚀 开始逐点导航，共 {total_poses} 个目标点")

        for idx, pose in enumerate(pose_list):
            print(f"\n📍 导航到第 {idx + 1}/{total_poses} 个目标点...")

            # 构造单点 pose list
            if isinstance(pose, dict):
                single_pose = pose
            else:
                single_pose = {
                    "x": pose[0], "y": pose[1], "z": pose[2],
                    "q_x": pose[3], "q_y": pose[4], "q_z": pose[5], "q_w": pose[6]
                }

            poses_json = {"poses": [single_pose]}

            # 写入临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(poses_json, f)
                temp_file = f.name

            # 启动单点导航
            cmd = [self.executable, 'start', temp_file, str(speed), str(mode), str(loop_mode)]
            nav_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 等待导航完成
            stdout, stderr = nav_process.communicate()
            ret = nav_process.returncode

            if ret == 0:
                print(f"✅ 已到达第 {idx + 1}/{total_poses} 个目标点")

                # 等待机械狗稳定
                if wait_stable_time > 0:
                    print(f"⏳ 等待 {wait_stable_time}s 稳定...")
                    time.sleep(wait_stable_time)

                # 拍照
                if photo_on_arrival:
                    self._take_photo(idx)
            else:
                print(f"❌ 导航到第 {idx + 1} 个点失败 (returncode={ret})")
                if stderr:
                    print(f"   stderr: {stderr.strip()}")
                continue

        # 所有点导航完成
        print(f"\n🎉 逐点导航完成，共 {total_poses} 个点")
        self._send_arrived()

    def _take_photo(self, pose_index):
        """拍照并保存"""
        import cv2
        import base64
        import numpy as np

        if not self._cam:
            print("⚠️ 相机未设置，跳过拍照")
            return

        timestamp = int(time.time() * 1000)
        print(f"📸 正在拍照 (第 {pose_index + 1} 个点)...")

        try:
            # ===== 1. 获取 RGB 和深度图 =====
            rgbs, depths, _ = self._cam.get_images(num_frames=1)
            if not rgbs:
                print("⚠️ 相机无数据，跳过拍照")
                return

            rgb_img = rgbs[-1]
            depth_img = depths[-1] if depths else None

            # RGB 编码
            _, jpeg_buf = cv2.imencode('.jpg', rgb_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
            rgb_b64 = base64.b64encode(jpeg_buf).decode('utf-8')

            # 深度图直接保存原始数据
            depth_b64 = None
            if depth_img is not None:
                # 直接编码原始深度图（uint16）
                _, depth_buf = cv2.imencode('.png', depth_img)
                depth_b64 = base64.b64encode(depth_buf).decode('utf-8')

            # ===== 2. 保存图片到本地 =====
            save_dir = "/home/unitree/photos"
            os.makedirs(save_dir, exist_ok=True)

            # 保存 RGB
            rgb_filename = f"nav_photo_{pose_index + 1}_{timestamp}.jpg"
            rgb_path = os.path.join(save_dir, rgb_filename)
            with open(rgb_path, 'wb') as f:
                f.write(base64.b64decode(rgb_b64))
            print(f"   RGB 已保存: {rgb_path}")

            # 保存深度图
            if depth_b64:
                depth_filename = f"nav_depth_{pose_index + 1}_{timestamp}.png"
                depth_path = os.path.join(save_dir, depth_filename)
                with open(depth_path, 'wb') as f:
                    f.write(base64.b64decode(depth_b64))
                print(f"   深度图已保存: {depth_path}")

        except Exception as e:
            print(f"❌ 拍照失败: {e}")
            import traceback
            traceback.print_exc()

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
