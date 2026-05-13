import os
import sys
import base64
import threading
import wave
import tempfile
import dashscope

from dashscope.audio.qwen_tts_realtime import *

# 👇 导入你已经在 server 中验证过可以出声的播放模块
sys.path.insert(0, '/home/unitree/dky/go2_python_sdk2')
from play_audio import play_audio

def init_dashscope_api_key():
    if 'DASHSCOPE_API_KEY' in os.environ:
        dashscope.api_key = os.environ['DASHSCOPE_API_KEY']
    else:
        dashscope.api_key = 'sk-10c321e6f4ee425095605a75cb4aa3ec'

class MyCallback(QwenTtsRealtimeCallback):
    def __init__(self):
        self.complete_event = threading.Event()
        # 用 bytearray 收集音频流，彻底抛弃会报错的 pyaudio
        self.audio_bytes = bytearray()

    def on_open(self):
        print("✅ TTS连接成功 (处理中...)")

    def on_close(self, code, msg):
        pass

    def on_event(self, response):
        try:
            event_type = response["type"]

            if event_type == "session.created":
                pass
            elif event_type == "response.audio.delta":
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
    """把原本在外面的初始化拿到这里，每次说话都建立一个新 Session"""
    callback = MyCallback()

    qwen_tts_realtime = QwenTtsRealtime(
        model="qwen-tts-realtime",
        callback=callback,
        url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    )

    qwen_tts_realtime.connect()

    # 原封不动保留你的设定
    qwen_tts_realtime.update_session(
        voice="Cherry",
        response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
        mode="streaming",
        instructions="语气可爱一点，适合用来给考拉配音"
    )

    qwen_tts_realtime.append_text(text)
    qwen_tts_realtime.finish()  # 告知服务器这句话结束了

    # 等待语音全部接收完毕
    callback.wait_for_finished()

    # ====== 接收完毕后，保存并用机器狗喇叭播放 ======
    if len(callback.audio_bytes) > 0:
        handle, tmp_wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(handle)
        
        # 写入 WAV 文件
        with wave.open(tmp_wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(callback.audio_bytes)
            
        print("🔊 播放语音...")
        try:
            # 使用机器狗原生播放命令
            play_audio(tmp_wav_path)
        except Exception as e:
            print(f"❌ 播放失败: {e}")
        finally:
            try:
                os.remove(tmp_wav_path)
            except:
                pass


if __name__ == "__main__":
    init_dashscope_api_key()

    print("\n🎤 输入文字就会说话 (Cherry)")
    print("输入 exit 退出\n")

    while True:
        try:
            text = input("你说: ").strip()

            if not text:
                continue

            if text.lower() in ["exit", '退出', 'bye']:
                speak_with_cherry("お兄様が大好きです，Mamba out")
                print("👋 拜拜")
                break
            
            # 使用单独的函数处理每次说话
            speak_with_cherry(text)
            
        except KeyboardInterrupt:
            print("\n程序中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")