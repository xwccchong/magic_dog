#!/usr/bin/env python3
import time
from unitree_nav import AsyncNavigationManager

nav = AsyncNavigationManager()

# 位姿列表
x1 = 2.28319; y1 = -0.62115; z1 = 0.048983
qx1= 0.0708168; qy1 = 0.101779; qz1 = -0.664117; qw1 = 0.737276

x2 = 4.96802; y2 = -0.0545474; z2 = 0.0722993
qx2 = -0.0970867; qy2 = 0.105798; qz2 = 0.706048; qw2 = 0.693454

poses1 = [(x1,y1,z1,qx1,qy1,qz1,qw1)]
poses2 = [(x2,y2,z2,qx2,qy2,qz2,qw2)]

# 启动导航
print("开始导航...")
nav.start_async(poses1, speed=0.5)

# 导航 5 秒
print("导航中...")
time.sleep(3)

# 暂停
print("暂停导航...")
nav.pause()

# 暂停 3 秒
print("暂停中...")
time.sleep(3)

# 恢复
nav.start_async(poses2, speed=0.5)
print("恢复导航...")
nav.resume()

# 等待完成
print("等待完成...")
nav.wait()

print("✓ 完成!")