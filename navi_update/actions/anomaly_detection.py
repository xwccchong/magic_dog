# -*- coding: utf-8 -*-
"""
异常检测动作：拍照 + LLM 视觉分析
"""
import cv2
import base64
import json
import time

from agent.utils.anomaly_detection import detect_anomaly


async def execute(cam, websocket, data, inspection_results):
    """
    拍照(暂不发送server) + 异常检测，结果追加到 inspection_results。
    websocket 参数保留，未来使用。
    """
    location = data.get("location", "未指定")
    print(f"🔍 异常检测 ({location}): 正在拍照并分析...")
    rgbs, _, _ = cam.get_images(num_frames=1)
    if not rgbs:
        print("⚠️ 相机无数据，跳过异常检测")
        return

    _, jpeg_buf = cv2.imencode('.jpg', rgbs[-1], [cv2.IMWRITE_JPEG_QUALITY, 85])
    img_b64 = base64.b64encode(jpeg_buf).decode('utf-8')

    # 通过 websocket 发送
    if websocket:
        await websocket.send(json.dumps({
            "type": "photo",
            "data": img_b64,
            "timestamp": time.time()
        }))
        print("   ✓ 多角度拼接图像已发送至服务端")
    else:
        print("   ⚠️ WebSocket 未连接，无法发送图像")

    result = detect_anomaly(img_b64)

    if result:
        result["location"] = location
        inspection_results.append(result)
        print(f"   📝 巡检结果已记录 (第{len(inspection_results)}个点)")
    else:
        print("⚠️ 异常检测失败，跳过")
