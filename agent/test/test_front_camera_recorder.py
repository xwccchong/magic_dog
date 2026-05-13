#!/usr/bin/env python3
"""测试机器狗头部相机录制"""
import time
import sys
sys.path.insert(0, '/home/unitree/unitree_sdk2_python/agent/level2')
from mp_front_camera_recorder import FrontCameraRecorder

recorder = FrontCameraRecorder(
    save_dir='/home/unitree/unitree_sdk2_python/agent/test/videos',
    resolution='720p',
)

print("Starting recorder...")
recorder.start(timeout=10)
print('Recording started, waiting 15 seconds...')
time.sleep(15)
print(f'Stopping...')
recorder.stop()
print('Done!')
