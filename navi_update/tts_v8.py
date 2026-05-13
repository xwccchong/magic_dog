import os
import sys
import base64
import threading
import wave
import tempfile
import time
import dashscope

from dashscope.audio.qwen_tts_realtime import *

# ==== 引入 Unitree Go2 通信 SDK ====
sys.path.insert(0, '/home/unitree/dky/go2_python_sdk2')
from unitree_sdk2py.core.dds.channel import DDSChannelFactoryInitialize
from unitree_sdk2py.sdk.sdk import create_standard_sdk
from unitree_sdk2py.go2.audiohub.audiohub_client import AudioHubClient

# 全局机器人音频客户端（保持单例长连接，消灭每次播放时的几秒启动延迟）
go2_audio_client = None

def init_dashscope_api_key():
    if 'DASHSCOPE_API_KEY' in os.environ:
        dashscope.api_key = os.environ['DASHSCOPE_API_KEY']
    else:
        dashscope.api_key = 'sk-10c321e6f4ee425095605a75cb4aa3ec'

def init_go2_audio():
    """仅在最开始启动一次 SDK 连接，后续永远复用"""
    global go2_audio_client
    if go2_audio_client is None:
        print("\n⏳ 正在建立与机器狗底层发声核心的极速网络连接...")
        try:
            sdk = create_standard_sdk('UnitreeGo2SDK')
            # 绑定 eth0 防止有些板子网络漂移连不上
            communicator = DDSChannelFactoryInitialize(domainId=0, networkInterface="eth0")
            robot = sdk.create_robot(communicator, serialNumber='B42D2000XXXXXXXX')
            
            go2_audio_client = robot.ensure_client(AudioHubClient.default_service_name)
            go2_audio_client.SetTimeout(3.0)
            go2_audio_client.Init()
            print("✅ 机器狗扬声器连接成功！时刻待命！\n")
        except Exception as e:
            print(f"❌ 初始化狗子音频核心失败: {e}")

class MyCallback(QwenTtsRealtimeCallback):
    def __init__(self):
        self.complete_event = threading.Event()
        self.audio_bytes = bytearray()

    def on_open(self):
        pass # 静默执行，不打印杂乱输出

    def on_close(self, code, msg):
        pass

    def on_event(self, response):
        try:
            event_type = response["type"]
            if event_type == "response.audio.delta":
                # 把大模型发回来的声音碎片拼起来
                audio = base64.b64decode(response["delta"])
                self.audio_bytes.extend(audio)
            elif event_type == "session.finished":
                self.complete_event.set()
        except Exception as e:
            print("error:", e)

    def wait_for_finished(self):
        self.complete_event.wait()

def speak_with_cherry(text):
    """急速合成并直接推送底层，不借用外部任何缓慢脚手架"""
    global go2_audio_client
    
    # 第一次没连接的话补连一下
    if go2_audio_client is None:
        init_go2_audio()
        
    tts_start_time = time.time()
    callback = MyCallback()
    
    qwen_tts_realtime = QwenTtsRealtime(
        model="qwen-tts-realtime",
        callback=callback,
        url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    )
    
    try:
        qwen_tts_realtime.connect()
        qwen_tts_realtime.update_session(
            voice="Cherry",
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode="streaming",
            instructions="语气可爱霸道一点，简短回复。"
        )
        qwen_tts_realtime.append_text(text)
        qwen_tts_realtime.finish()  
        
        callback.wait_for_finished()
        wait_cost = time.time() - tts_start_time
        
        # 如果生成了声音，开始极速操作（抛弃缓慢的 pydub 计算）
        if len(callback.audio_bytes) > 0:
            # 1. 纯手工通过文件流写 wav，速度快于 pydub 10倍以上
            handle, tmp_wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(handle)
            
            with wave.open(tmp_wav_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(callback.audio_bytes)
                
            # 2. 纯数学计算音频长度：字节数 / (采样率24000 * 16位(2个字节长度))
            duration = len(callback.audio_bytes) / (24000.0 * 2.0)
            
            # 3. 直抵核心，瞬间通过现成的 DDS 塞给狗的扩展坞
            if go2_audio_client:
                print(f"🔊 狗扬声器动作: [TTS等待: {wait_cost:.2f}s] [时常: {duration:.2f}s]")
                go2_audio_client.MegaphoneEnter()
                go2_audio_client.MegaphoneUpload(tmp_wav_path)
                
                # 刚好等音频播完就撤退
                time.sleep(duration + 0.2)
                go2_audio_client.MegaphoneExit()
                
            try:
                os.remove(tmp_wav_path)
            except:
                pass
                
    except Exception as e:
        print(f"说话遇到错误: {e}")

if __name__ == "__main__":
    init_dashscope_api_key()
    init_go2_audio()  # 打开脚本就立刻预热 SDK

    print("\n🎤 输入文字就会说话 (全内存加速 + DDS长图直入版)")
    print("输入 exit 退出\n")

    while True:
        try:
            text = input("你说: ").strip()
            if not text:
                continue

            if text.lower() in ["exit", '退出', 'bye']:
                speak_with_cherry("拜拜啦！")
                print("👋 拜拜")
                break
                
            speak_with_cherry(text)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"发生错误: {e}")