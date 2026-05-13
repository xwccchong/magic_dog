# -*- coding: utf-8 -*-
"""
拍照动作：拍照并发送 JPEG base64 到服务端（包含 RGB 和深度图）
"""
import json
import time
import cv2
import base64
import numpy as np


async def execute(cam, websocket, data=None):
    """拍照并发送到服务端，返回 RGB 和深度图的 base64 字符串

    Args:
        cam: 相机实例
        websocket: WebSocket 连接
        data: 可选数据字典，可包含 "location" 等字段

    Returns:
        dict: {"rgb": rgb_b64, "depth": depth_b64} 或 None
    """
    # 确保 data 不为 None
    if data is None:
        data = {}

    location = data.get("location", "未指定")
    print(f"📸 正在拍照... (位置: {location})")

    rgbs, depths, _ = cam.get_images(num_frames=1)
    if not rgbs:
        print("⚠️ 相机无数据")
        return None

    # RGB 图像编码为 JPEG
    _, jpeg_buf = cv2.imencode('.jpg', rgbs[-1], [cv2.IMWRITE_JPEG_QUALITY, 85])
    rgb_b64 = base64.b64encode(jpeg_buf).decode('utf-8')

    # 深度图编码（保存原始深度数据）
    depth_b64 = None
    if depths:
        depth_img = depths[-1]
        # 直接编码原始深度图（uint16）
        _, depth_buf = cv2.imencode('.png', depth_img)
        depth_b64 = base64.b64encode(depth_buf).decode('utf-8')

    if websocket:
        payload = {
            "type": "photo",
            "data": rgb_b64,
            "location": location,
            "timestamp": time.time()
        }
        # 如果有深度图，添加到 payload
        if depth_b64:
            payload["depth_data"] = depth_b64

        await websocket.send(json.dumps(payload))
        print(f"✓ 照片已发送至服务端 (位置: {location}, 含深度图: {depth_b64 is not None})")
    else:
        print("⚠️ WebSocket 未连接，无法发送照片")

    return {"rgb": rgb_b64, "depth": depth_b64}
