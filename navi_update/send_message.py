import asyncio
import threading
import websockets
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_back_ws(msg="play"):
    """异步、非阻塞地通过 websocket 发送消息"""
    def _send():
        async def _async_send():
            uri = "ws://172.50.0.211:8765"
            try:
                async with websockets.connect(uri) as ws:
                    await ws.send(msg)
                    logger.info(f"✓ 发送消息成功: {msg}")
            except Exception as e:
                logger.warning(f"❌ send_back_ws failed: {e}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_async_send())
        loop.close()
    
    threading.Thread(target=_send, daemon=True).start()


if __name__ == "__main__":
    # 测试发送消息
    send_back_ws("play")
    
    # 等待线程完成（因为是 daemon 线程，主线程结束会自动终止）
    import time
    time.sleep(2)  # 等待消息发送完成
    
    print("测试完成")