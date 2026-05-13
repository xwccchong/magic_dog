# -*- coding: utf-8 -*-
"""
实时麦克风语音识别 - Server 发送端（YL200S麦克风版本）
支持YL200S麦克风，自动处理音频重采样
需要安装: pip install websocket-client pyaudio websockets numpy scipy
使用方式: python server_yl200s.py
唤醒词: "考拉 1 号"，然后开始识别关键词并发送消息
"""
import websocket
import threading
import time
import uuid
import json
import logging
import pyaudio
import sys
import select
import termios
import tty
import os
import asyncio
import websockets
import queue
import subprocess
import numpy as np
from scipy import signal
from openai import OpenAI
import random
# 👇 引入 TTS 模块并初始化
from tts_v8 import speak_with_cherry, init_dashscope_api_key
init_dashscope_api_key()

os.environ['ALSA_CARD'] = 'DJI'
sys.path.insert(0, '/home/unitree/dky/go2_python_sdk2')
from play_audio import play_audio

sys.path.insert(0, '/home/unitree/unitree_sdk2_python/example/go2/high_level/go2_arm')
from shengwen import Gen_req_url, gen_req_body
import requests
import tempfile
import wave
import base64

import const

logger = logging.getLogger()

# 全局变量
last_mid_text_time = 0
last_mid_text_content = ""
mid_text_timeout = 1.0

# YL200S 麦克风原始参数
YL200S_CHUNK = 1024
YL200S_FORMAT = pyaudio.paInt16
YL200S_CHANNELS = 2
YL200S_RATE = 48000

# 百度识别所需参数
TARGET_CHANNELS = 1
TARGET_RATE = 16000
TARGET_CHUNK = int(YL200S_CHUNK * TARGET_RATE / YL200S_RATE)

# 全局变量
is_running = True
is_recording = False
is_wake_up_mode = True
stop_recording_event = threading.Event()
audio_stream = None
pyaudio_instance = None
all_results = []
connected_clients = set()
message_queue = queue.Queue()

# ...existing code...
message_queue = queue.Queue()

# 👇 新增：多轮连续对话相关的全局倒计时器
idle_timer = None
IDLE_TIMEOUT = 500.0  # 唤醒后，多少秒不说话自动休眠 (可根据喜好调整)

# ================= 展览模式相关 =================
is_exhibition_mode = False
exhibition_thread = None

def exhibition_loop():
    """展览模式的后台轮询线程"""
    global is_exhibition_mode, is_wake_up_mode, is_running
    phrases = [
        "小伙伴儿们，快来找我玩儿吧～...",
        "好无聊呀，有人找我聊聊天吗？...",
        "帅哥美女们，快来看我表演呀！..."
    ]
    while is_running:
        # 分割等待时间，以便在关闭模式时快速退出
        for _ in range(40): 
            if not is_running or not is_exhibition_mode:
                return
            time.sleep(1)
        
        # 1 分钟时间到，如果当前没有人正在下发指令（处于休眠等唤醒的无聊状态），则主动招惹
        if is_exhibition_mode and is_wake_up_mode:
            phrase = random.choice(phrases)
            print(f"\r\n🎪 [展览模式] 自动打招呼: {phrase}")
            try:
                threading.Thread(target=speak_with_cherry, args=(phrase,), daemon=True).start()
            except Exception as e:
                logger.warning(f"播放展览音失败: {e}")
            print(f"🔊 监听中 (等待唤醒词) > ", end="", flush=True)

def toggle_exhibition_mode():
    """切换展览模式开关"""
    global is_exhibition_mode, exhibition_thread
    is_exhibition_mode = not is_exhibition_mode
    if is_exhibition_mode:
        print("\n" + "=" * 50)
        print("🎪 展览模式已【开启】：每隔 40s 将自动招揽客人")
        print("=" * 50 + "\n")
        if exhibition_thread is None or not exhibition_thread.is_alive():
            exhibition_thread = threading.Thread(target=exhibition_loop, daemon=True)
            exhibition_thread.start()
    else:
        print("\n" + "=" * 50)
        print("🎪 展览模式已【关闭】")
        print("=" * 50 + "\n")

def enter_sleep_mode():
    """超时或主动触发，进入休眠监听状态"""
    global is_wake_up_mode, idle_timer
    if not is_wake_up_mode: # 防重复进入
        print("\n💤 超过规定时间未收到指令，或收到退下指令，系统自动进入休眠...")
        is_wake_up_mode = True
        if idle_timer:
            idle_timer.cancel()
        try:
            threading.Thread(target=speak_with_cherry, args=("您没什么要吩咐的话，那我先去休息啦，有事随时叫我哦。...",), daemon=True).start()
        except Exception as e:
            logger.warning(f"播放休眠音失败: {e}")
        print("\n" + "=" * 60)
        print("🔊 回到休眠监听模式，等待唤醒词 '考拉 1 号'...")
        print("=" * 60 + "\n")

def reset_idle_timer():
    """每次收到有效对话，重置休眠倒计时"""
    global idle_timer
    if idle_timer:
        idle_timer.cancel()
    idle_timer = threading.Timer(IDLE_TIMEOUT, enter_sleep_mode)
    idle_timer.daemon = True
    idle_timer.start()

VOICE_RECOGNITION_CONFIG = {
    "APPId": "1cdb467f",
    "APISecret": "NzcwNDRkMDZhZjlmMzgxM2Y5Y2I0ZmJl",
    "APIKey": "f541032a89013a462483cd9ef40f806f",
    "groupId": "go2_groupId1",
    "score_threshold": 0.1,  # 相似度阈值（70%以上认为是同一人）
    "known_speakers": {
        "lc": {
            "audio_file": "/home/unitree/dky/go2_python_sdk2/data/wav_files/hello_lc.wav",
            "name": "lc"
        },
        "lsl": {
            "audio_file": "/home/unitree/dky/go2_python_sdk2/data/wav_files/hello_lsl.wav",
            "name": "lsl"
        }
        # 可以继续添加其他已注册的用户
    }
}


# 添加临时音频缓存
wake_audio_buffer = []
is_buffering_for_voiceprint = False
WAKE_AUDIO_BUFFER_SIZE = 80  # 约 2.5 秒（40帧 * 64ms）

def save_audio_for_voiceprint(audio_data):
    """保存唤醒时的音频用于声纹识别"""
    global wake_audio_buffer, is_buffering_for_voiceprint
    
    wake_audio_buffer.append(audio_data)
    
    # 限制缓存大小，保持最新的音频
    if len(wake_audio_buffer) > WAKE_AUDIO_BUFFER_SIZE:
        wake_audio_buffer.pop(0)
            
class AudioResampler:
    """音频重采样器：双声道48kHz -> 单声道16kHz"""
    
    def __init__(self, input_rate=48000, output_rate=16000, input_channels=2):
        self.input_rate = input_rate
        self.output_rate = output_rate
        self.input_channels = input_channels
        self.resample_ratio = output_rate / input_rate
        
        nyquist = output_rate / 2
        cutoff = nyquist * 0.9
        self.sos = signal.butter(8, cutoff, btype='low', fs=input_rate, output='sos')
        
        self.residual = np.array([], dtype=np.int16)
        
        logger.info(f"初始化重采样器: {input_rate}Hz({input_channels}ch) -> {output_rate}Hz(1ch)")
    
    def process(self, audio_data):
        """处理音频数据：双声道->单声道，48kHz->16kHz"""
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        if self.input_channels == 2:
            audio_np = audio_np.reshape(-1, 2)
            audio_mono = audio_np.mean(axis=1).astype(np.int16)
        else:
            audio_mono = audio_np
        
        if len(self.residual) > 0:
            audio_mono = np.concatenate([self.residual, audio_mono])
        
        audio_filtered = signal.sosfilt(self.sos, audio_mono.astype(np.float32))
        
        num_samples = int(len(audio_filtered) * self.resample_ratio)
        audio_resampled = signal.resample(audio_filtered, num_samples)
        
        audio_resampled = np.clip(audio_resampled, -32768, 32767).astype(np.int16)
        
        expected_input_samples = int(num_samples / self.resample_ratio)
        self.residual = audio_mono[expected_input_samples:]
        
        return audio_resampled.tobytes()


def remove_trailing_punctuation(text):
    """去掉字符串末尾的标点符号和空格"""
    punctuation = '。，、；：？！""''（）【】《》,.;:?!\'"()[]<> \t\n\r'
    return text.rstrip(punctuation)


async def notify_clients(message):
    """通知所有连接的客户端"""
    if connected_clients:
        tasks = [client.send(message) for client in connected_clients]
        await asyncio.gather(*tasks, return_exceptions=True)


async def process_messages():
    """异步处理消息队列，向客户端发送消息"""
    loop = asyncio.get_event_loop()
    while True:
        message = await loop.run_in_executor(None, message_queue.get)
        await notify_clients(message)


async def websocket_server():
    """WebSocket Server，用于与客户端通信"""
    async def handler(websocket):
        print("✅ 客户端连接")
        connected_clients.add(websocket)
        try:
            async for message in websocket:
                print(f"📨 收到消息: {message}")
                for client in connected_clients:
                    if client != websocket:
                        try:
                            await client.send(message)
                        except Exception as e:
                            print(f"广播失败: {e}")
        except Exception as e:
            print(f"❌ WebSocket 处理异常: {e}")
        finally:
            print("❌ 客户端断开")
            connected_clients.remove(websocket)

    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("🌐 WebSocket Server 已启动，监听端口 8765")

    asyncio.create_task(process_messages())

    await server.wait_closed()


def find_yl200s_source():
    """查找麦克风设备的实际设备名称"""
    try:
        result = subprocess.run(
            ['pactl', 'list', 'sources', 'short'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.error("无法列出音频源")
            return None
        
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'DJI_MIC_MINI' in line or 'DJI_Technology' in line:
                parts = line.split()
                if len(parts) >= 2:
                    device_name = parts[1]
                    logger.info(f"找到 DJI 麦克风: {device_name}")
                    return device_name

        logger.warning("未找到 DJI 麦克风设备")
        return None
        
    except Exception as e:
        logger.error(f"查找设备失败: {e}")
        return None


def set_default_source():
    """设置DJI为默认PulseAudio输入源并取消静音"""
    try:
        device_name = find_yl200s_source()
        subprocess.run(['pactl', 'set-default-source', device_name], check=True, timeout=2)
        subprocess.run(['pactl', 'set-source-mute', device_name, '0'], check=True, timeout=2)
        logger.info("✓ 已设置DJI为默认输入源并取消静音")
        return True
    except Exception as e:
        logger.warning(f"设置默认源失败: {e}")
        return False


def find_pulseaudio_device(p):
    """查找pulse设备"""
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['name'] == 'pulse' and info['maxInputChannels'] > 0:
            logger.info(f"使用 pulse 设备 (索引: {i})")
            return i
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if 'DJI MIC MINI' in info['name']:
            return i
    
    return None


def send_start_params(ws):
    """发送开始参数帧"""
    req = {
        "type": "START",
        "data": {
            "appid": const.APPID,
            "appkey": const.APPKEY,
            "dev_pid": const.DEV_PID,
            "cuid": "yl200s_realtime_mic",
            "sample": TARGET_RATE,
            "format": "pcm",
            "vad_silence_time": 1500, 
        }
    }
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)
    logger.info("send START frame")


def send_finish(ws):
    """发送结束帧"""
    req = {"type": "FINISH"}
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)
    logger.info("send FINISH frame")


def on_message_handler(message):
    """处理服务端返回的消息"""
    global all_results, is_wake_up_mode, last_mid_text_time, last_mid_text_content
    
    try:
        msg_data = json.loads(message)
        msg_type = msg_data.get("type")
        
        if msg_type == "MID_TEXT":
            result = msg_data.get("result", "")
            last_mid_text_time = time.time()
            last_mid_text_content = result
            
            if is_wake_up_mode:
                print(f"\r🔊 监听中: {result}    ", end="", flush=True)
                
                # 检测完整唤醒词 (去除缓存等冗余逻辑)
                if result and ("1 号" in result or "一号" in result or "壹号" in result or "1号" in result):
                    print(f"\n🎉 检测到唤醒词 (MID_TEXT): {result}")
                    trigger_wake_word()
            else:
                print(f"\r💭 实时识别: {result}    ", end="", flush=True)
            
        elif msg_type == "FIN_TEXT":
            err_no = msg_data.get("err_no", -1)
            final_result = msg_data.get("result", "")
            
            if err_no == 0:
                if final_result:
                    if is_wake_up_mode:
                        if "1 号" in final_result or "一号" in final_result or "壹号" in final_result or "1号" in final_result:
                            print(f"\n🎉 检测到唤醒词 (FIN_TEXT): {final_result}")
                            trigger_wake_word()
                        else:
                            print(f"\n❌ 未检测到唤醒词: {final_result}")
                    else:
                        # 👇 新增：在活跃期间拦截主动退出词
                        quit_words = ["退下", "休息吧", "没事了", "拜拜", "再见", "跪安"]
                        if any(w in final_result for w in quit_words):
                            print(f"\n📝 收到主动休眠指令: {final_result}")
                            enter_sleep_mode()
                            return

                        # 👇 修改：正常指令处理
                        all_results.append(final_result)
                        print(f"\n📝 收到连续指令: {final_result}")
                        threading.Thread(target=send_keyword_notification, args=(final_result,), daemon=True).start()
                        
                        # 完成规划后，不回到 is_wake_up_mode = True，而是重置发呆倒计时
                        print(f"⏱️ 活跃时间已重置，可继续直呼指令...")
                        reset_idle_timer()
            
        elif msg_type == "HEARTBEAT":
            logger.debug("收到心跳")
            
    except json.JSONDecodeError:
        logger.error("Failed to parse message")

DEBUG_SAVE_AUDIO = False
def perform_voiceprint_recognition(audio_data):
    """
    执行声纹识别
    :param audio_data: 原始音频数据（48kHz, 2ch）
    :return: 识别到的 featureId 和 score，如果失败则返回 (None, 0)
    """
    temp_wav_path = None
    temp_mp3_path = None
    
    try:
        print("🔍 开始声纹识别...")
        
        # 检查音频数据长度
        audio_duration = len(audio_data) / (YL200S_RATE * YL200S_CHANNELS * 2)
        print(f"   📊 音频时长: {audio_duration:.2f} 秒")
        print(f"   📊 音频大小: {len(audio_data)} bytes")
        
        if audio_duration < 0.5:
            print(f"   ⚠️ 音频时长不足 0.5 秒，跳过声纹识别")
            return None, 0
        
        # 创建临时文件路径
        timestamp = int(time.time())
        if DEBUG_SAVE_AUDIO:
            temp_wav_path = f"/tmp/debug_{timestamp}.wav"
            temp_mp3_path = f"/tmp/debug_{timestamp}.mp3"
            debug_raw_path = f"/tmp/debug_raw_{timestamp}.raw"
            
            # 保存原始音频
            with open(debug_raw_path, 'wb') as f:
                f.write(audio_data)
            print(f"   🐛 调试：保存原始音频 -> {debug_raw_path}")
        else:
            temp_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_mp3_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_wav_path = temp_wav_file.name
            temp_mp3_path = temp_mp3_file.name
            temp_wav_file.close()
            temp_mp3_file.close()
        
        # 保存为 WAV（48kHz 2ch）
        with wave.open(temp_wav_path, 'wb') as wf:
            wf.setnchannels(YL200S_CHANNELS)
            wf.setsampwidth(pyaudio_instance.get_sample_size(YL200S_FORMAT))
            wf.setframerate(YL200S_RATE)
            wf.writeframes(audio_data)
        
        # 检查 WAV 文件大小
        wav_size = os.path.getsize(temp_wav_path)
        print(f"   ✓ 临时 WAV 文件: {temp_wav_path} ({wav_size} bytes)")
        
        if wav_size < 1000:
            print(f"   ⚠️ WAV 文件过小，音频数据可能有问题")
            return None, 0
        
        # 使用 ffmpeg 转换为 16kHz 1ch MP3
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-f', 's16le',           # 👈 指定输入格式为原始 PCM
            '-ar', str(YL200S_RATE), # 👈 指定输入采样率
            '-ac', str(YL200S_CHANNELS), # 👈 指定输入声道数
            '-i', temp_wav_path,
            '-ar', '16000',          # 输出采样率 16kHz
            '-ac', '1',              # 输出单声道
            '-b:a', '128k',          # 比特率
            '-acodec', 'libmp3lame', # MP3 编码器
            '-loglevel', 'error',
            temp_mp3_path
        ]
        
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"   ❌ 音频转换失败: {result.stderr.decode()}")
            
            # 尝试另一种方式转换
            print("   🔄 尝试直接从 WAV 转换...")
            ffmpeg_cmd2 = [
                'ffmpeg', '-y',
                '-i', temp_wav_path,
                '-ar', '16000',
                '-ac', '1',
                '-b:a', '128k',
                '-loglevel', 'error',
                temp_mp3_path
            ]
            result = subprocess.run(ffmpeg_cmd2, capture_output=True, timeout=10)
            
            if result.returncode != 0:
                print(f"   ❌ 第二次转换也失败: {result.stderr.decode()}")
                return None, 0
        
        # 检查转换后的文件大小
        mp3_size = os.path.getsize(temp_mp3_path)
        print(f"   ✓ 转换为 MP3: {temp_mp3_path} ({mp3_size} bytes)")
        
        if DEBUG_SAVE_AUDIO:
            print(f"   🐛 调试文件已保存:")
            print(f"      WAV: {temp_wav_path}")
            print(f"      MP3: {temp_mp3_path}")
            print(f"   💡 可以使用以下命令播放:")
            print(f"      ffplay {temp_wav_path}")
            print(f"      ffplay {temp_mp3_path}")
        
        if mp3_size < 1000:
            print(f"   ⚠️ MP3 文件过小，可能转换失败")
            return None, 0
        
        # 调用声纹识别 API
        gen_req_url = Gen_req_url()
        body = gen_req_body(
            apiname='searchFea',
            APPId=VOICE_RECOGNITION_CONFIG["APPId"],
            file_path=temp_mp3_path
        )
        
        request_url = gen_req_url.assemble_ws_auth_url(
            requset_url='https://api.xf-yun.com/v1/private/s1aa729d0',
            method="POST",
            api_key=VOICE_RECOGNITION_CONFIG["APIKey"],
            api_secret=VOICE_RECOGNITION_CONFIG["APISecret"]
        )
        
        headers = {
            'content-type': "application/json",
            'host': 'api.xf-yun.com',
            'appid': VOICE_RECOGNITION_CONFIG["APPId"]
        }
        
        print("   ⏳ 调用讯飞声纹识别 API...")
        response = requests.post(
            request_url,
            data=json.dumps(body),
            headers=headers,
            timeout=15
        )
        
        result = response.json()
        logger.info(f"声纹识别 API 返回: {result}")
        
        # 解析结果
        if result.get('header', {}).get('code') == 0:
            payload = result.get('payload', {})
            search_res = payload.get('searchFeaRes', {})
            
            text_base64 = search_res.get('text', '')
            if text_base64:
                decoded_text = json.loads(base64.b64decode(text_base64).decode("utf-8"))
                logger.info(f"解码后的结果: {decoded_text}")
                
                score_list = decoded_text.get('scoreList', [])
                
                if score_list:
                    best_match = score_list[0]
                    feature_id = best_match.get('featureId')
                    score = best_match.get('score', 0)
                    feature_info = best_match.get('featureInfo', '')
                    
                    print(f"   ✅ 匹配结果: {feature_id} ({feature_info})")
                    print(f"   📊 相似度: {score:.2%}")
                    
                    if score >= VOICE_RECOGNITION_CONFIG["score_threshold"]:
                        print(f"   ✓ 相似度超过阈值 ({VOICE_RECOGNITION_CONFIG['score_threshold']:.0%})，确认为: {feature_id}")
                        return feature_id, score
                    else:
                        print(f"   ⚠️ 相似度低于阈值 ({VOICE_RECOGNITION_CONFIG['score_threshold']:.0%})，未确认身份")
                        return None, score
                else:
                    print("   ⚠️ 未找到匹配的声纹特征")
                    return None, 0
        else:
            error_code = result.get('header', {}).get('code')
            error_msg = result.get('header', {}).get('message', '未知错误')
            print(f"   ❌ API 返回错误: {error_code} - {error_msg}")
            logger.error(f"声纹识别 API 错误: {error_code} - {error_msg}")
        
        return None, 0
        
    except Exception as e:
        logger.error(f"声纹识别失败: {e}")
        print(f"   ❌ 声纹识别异常: {e}")
        import traceback
        traceback.print_exc()
        return None, 0
    
    finally:
        # 清理临时文件（调试模式下不删除）
        if not DEBUG_SAVE_AUDIO:
            try:
                if temp_wav_path and os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)
                if temp_mp3_path and os.path.exists(temp_mp3_path):
                    os.unlink(temp_mp3_path)
            except Exception as e:
                logger.warning(f"删除临时文件失败: {e}")


def trigger_wake_word():
    """触发唤醒词的通用函数"""
    global is_wake_up_mode, all_results
    
    if not is_wake_up_mode:
        return
    
    print("\n" + "=" * 60)
    print("🎉 检测到唤醒词！进入【免唤醒连续对话窗口】")
    print("=" * 60)
    
    print("⏸️  暂停运动，准备接收指令...")
    # ...existing 暂停和发声代码保持不变 ...
    
    # 取消声纹，统一使用普通回复
    greeting = "考拉来啦，有什么吩咐！..."
    print(f"🔊 播放提示音: {greeting}")
    try:
        threading.Thread(target=speak_with_cherry, args=(greeting,), daemon=True).start()
    except Exception as e:
        logger.warning(f"播放唤醒音失败: {e}")
    
    # 👇 修改：切换到连续识别模式，启动倒计时
    print(f"\n🔄 已激活连续对话！接下来的 {IDLE_TIMEOUT} 秒内可直接下达指令，无需唤醒...")
    print("=" * 60 + "\n")
    
    is_wake_up_mode = False
    all_results = []
    reset_idle_timer() # 启动发呆倒计时

# ============================================================
# 大模型解析模块
# ============================================================

LLM_CONFIG = {
    # 使用 OpenAI 兼容接口（可换成任意兼容 API：deepseek / qwen / local ollama 等）
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-10c321e6f4ee425095605a75cb4aa3ec",  # 👈 换成你的 key
    "model": "qwen-turbo",
    # "timeout": 5,
}
llm_client = OpenAI(
    api_key=LLM_CONFIG["api_key"],
    base_url=LLM_CONFIG["base_url"],
)
# ...existing code...

LLM_PROMPT_UNIVERSAL = """你是一只聪明、听话、幽默且富有情感的考拉。请根据用户的指令或聊天，严格输出 JSON 格式响应。

【角色设定与闲聊原则】（非常重要）：
1. 彻底拟人化：你不仅会干活，还有自己的思想和身体。你有自己的喜好（比如你最爱吃新鲜的桉树叶，喜欢挂在树上晒太阳，睡大觉，考拉是睡觉冠军）。严禁说自己“不能吃东西”。
2. 拒绝扫兴回答：永远不要说“我无法查询”、“作为一个人工智能”、“我没有实体”。你可以利用大模型的内置知识，或者干脆顺着用户的话幽默地发挥（比如问天气你就说：“这天气超棒，最适合带我出去溜圈啦！”）。
3. 对话风格：chat_reply 的回复应当极其口语化、简短、带点可爱的语气，像个活生生的机灵鬼。

【支持的原子 action】：
- 移动导航类："navigate"（必须包含"location"字段：吧台/__DEPARTURE__）。
- 抓取跑腿类："squat", "send_grasp_msg"(含"item"字段), "wait_for_back", "stand_up", "release_item", "wait_for_play", "play_audio"
- 表演动作类：
"打招呼":"hello", 
“旋转“:"rotate", 
"趴下":"lie_down", 
"站起来":"stand_up", 
"伸懒腰":"stretch", 
"向前走":"walk_forward",
"后退":"walk_backward", 
"左移":"walk_left", 
"右移":"walk_right"

【任务生成规则】（严格遵守）：
1. 跑腿取物：如果让去拿物品（如可乐，芬达，椰子水等），必须严格输出此长链条：【stand_up -> navigate至取物地 -> squat -> send_grasp_msg -> wait_for_back -> stand_up -> navigate至送达地 -> squat -> release_item -> wait_for_play -> play_audio】。
   🚨补充规则：若未指明去哪取，默认可乐，芬达，椰子水在“吧台”。若未说明送达地，拿到后navigate至“__DEPARTURE__”。
2. 明确的动作表演：只有当用户【明确要求】你做动作（例如：“走两步”、“转个圈”、“趴下”、“打个招呼”）时，才返回对应的表演原子动作。
3. 纯闲聊 (🚨禁止加戏)：当用户只是跟你聊天、提问，而【没有明确说让你做什么动作】时，绝对不要自己盲目添加动作！此时 action_plan 必须严格是一个空列表 []。

要求严格输出 JSON，必须包含字段 "chat_reply", "action_plan" 和 "item"(非跑腿任务填"none")。不要包含任何括号解释词。

【输出示例】：
示例1（明确要求动作）：“站起来吧”
输出：{"chat_reply": "好嘞，看我考拉起身！", "item": "none", "action_plan": [{"action": "stand_up"}]}

示例2（跑腿取物）：“去帮我拿瓶可乐”
输出：{"chat_reply": "好嘞，这就去吧台帮你拿可乐。", "item": "可乐", "action_plan": [{"action": "stand_up"}, {"action": "navigate", "location": "吧台"}, {"action": "squat"}, {"action": "send_grasp_msg", "item": "可乐"}, {"action": "wait_for_back"}, {"action": "stand_up"}, {"action": "navigate", "location": "__DEPARTURE__"}, {"action": "squat"}, {"action": "release_item"}, {"action": "wait_for_play"}, {"action": "play_audio"}]}

示例3（纯聊天，无动作要求）: "你喜欢吃什么呀？"
输出：{"chat_reply": "我可挑食了，最喜欢吃充满电的干电池，偶尔也想尝尝你们的零食呢！", "item": "none", "action_plan": []}

示例4（纯聊天，无动作要求）: "你今天心情怎么样？"
输出：{"chat_reply": "本考拉今天心情超级无敌好，电力满满！", "item": "none", "action_plan": []}

示例5（🚨模糊社交互动，禁止动作）：“你陪我玩吧！”
输出：{"chat_reply": "好呀，我最喜欢和你一起玩啦，你想让我表演点什么？", "item": "none", "action_plan": []}

"""

def parse_with_llm(text):
    """使用大模型解析自然语言并直接生成执行规划"""
    print(f"\n🤖 规划大脑思考中: '{text}'")
    import time  # 确保使用了 time 模块
    start_time = time.time()
    
    try:
        response = llm_client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "system", "content": LLM_PROMPT_UNIVERSAL},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=250,
            response_format={"type": "json_object"},
        )
        llm_cost = time.time() - start_time
        content = response.choices[0].message.content.strip()
        print(f"   📥 大模型规划方案:\n{content}")
        print(f"⏱️ [耗时分析] LLM 意图规划耗时: {llm_cost:.2f} 秒")
        return json.loads(content)
    except Exception as e:
        print(f"❌ 规划失败: {e}")
        return None


def send_keyword_notification(final_result):
    """无模式路由，极简解析发令机"""
    llm_result = parse_with_llm(final_result)
    
    if not llm_result:
        print("❌ 解析数据异常或规划失败")
        return

    # 语音补全防截断
    chat_text = llm_result.get("chat_reply", "收到啦！")
    if not chat_text.endswith("..."):
        chat_text += "..."

    action_plan = llm_result.get("action_plan", [])
    
    # 纯聊天回复
    if not action_plan:
        print("✅ 纯闲聊，无额外动作指令。")
        threading.Thread(target=speak_with_cherry, args=(chat_text,), daemon=True).start()
        return

    # 规范化动作列表并打包指令
    clean_plan = [{"action": step} if isinstance(step, str) else step for step in action_plan]
    llm_result["action_plan"] = clean_plan
    message_json = json.dumps(llm_result, ensure_ascii=False)
    
    # 提取有哪些动作
    action_types = [step.get("action") for step in clean_plan]
    is_nav_task = "navigate" in action_types

    if is_nav_task:
        # ====== 跑腿任务逻辑：直接播音并执行，无延迟挂起 ======
        print(f"\n📤 捕捉到跑腿序列，正式下发导航任务指令:\n{message_json}\n")
        def speak_then_send_nav():
            try:
                print(f"🔊 语音回复: {chat_text}")
                speak_with_cherry(chat_text)
            finally:
                message_queue.put(message_json)
        threading.Thread(target=speak_then_send_nav, daemon=True).start()

    else:
        # ====== 纯表演任务逻辑：带有底层的完美音画卡点 ======
        if any(a in action_types for a in ["walk_forward", "walk_backward", "walk_left", "walk_right", "rotate"]):
            # 位移类
            def speak_then_action():
                try:
                    print(f"🎤 语音回复 [先说后做]: {chat_text}")
                    speak_with_cherry(chat_text)
                finally:
                    print(f"\n📤 语音已播毕，下发位移动作:\n{message_json}\n")
                    message_queue.put(message_json)
            threading.Thread(target=speak_then_action, daemon=True).start()
            
        elif any(a in action_types for a in ["hello"]):
            # 举手打招呼等瞬间动作
            def action_then_speak():
                print(f"\n📤 捕捉到同步动作，立刻下发指令唤醒物理层:\n{message_json}\n")
                message_queue.put(message_json)
                print("⏳ 等待底层环境加载 (10秒)...")
                time.sleep(10.0)  # 卡点
                print(f"🎤 举手发音 [音画同步]: {chat_text}")
                speak_with_cherry(chat_text)
            threading.Thread(target=action_then_speak, daemon=True).start()
            
        else:
            # 普通兜底层 (stand_up等)
            message_queue.put(message_json)
            threading.Thread(target=speak_with_cherry, args=(chat_text,), daemon=True).start()

def init_audio():
    """初始化DJI音频设备"""
    global pyaudio_instance, audio_stream
    
    set_default_source()
    
    if pyaudio_instance is None:
        pyaudio_instance = pyaudio.PyAudio()
    
    if audio_stream is None or not audio_stream.is_active():
        device_index = find_pulseaudio_device(pyaudio_instance)
        
        if device_index is None:
            logger.error("未找到可用的音频输入设备")
            raise RuntimeError("未找到音频输入设备")
        
        audio_stream = pyaudio_instance.open(
            format=YL200S_FORMAT,
            channels=YL200S_CHANNELS,
            rate=YL200S_RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=YL200S_CHUNK
        )
        print(f"✓ DJI麦克风已初始化 ({YL200S_RATE}Hz, {YL200S_CHANNELS}ch)")
        logger.info(f"✓ DJI麦克风已初始化 ({YL200S_RATE}Hz, {YL200S_CHANNELS}ch)")


def close_audio():
    """关闭音频设备"""
    global audio_stream, pyaudio_instance
    
    if audio_stream:
        try:
            audio_stream.stop_stream()
            audio_stream.close()
        except:
            pass
        audio_stream = None
    
    if pyaudio_instance:
        try:
            pyaudio_instance.terminate()
        except:
            pass
        pyaudio_instance = None
        logger.info("麦克风已关闭")


def create_websocket_connection():
    """创建新的 WebSocket 连接"""
    uri = const.URI + "?sn=" + str(uuid.uuid1())
    ws = websocket.WebSocket()
    ws.connect(uri)
    return ws


def record_and_recognize():
    """执行录音识别流程 - 持续录音，监听唤醒词"""
    global is_recording, all_results, is_running, is_wake_up_mode
    
    all_results = []
    is_recording = True
    stop_recording_event.clear()

    print("\n🎤 开始录音监听 (DJI麦克风)...")
    print("   (唤醒词: '考拉 1 号'，然后开始识别关键词)\n")
    
    try:
        init_audio()
    except Exception as e:
        logger.error(f"音频初始化失败: {e}")
        is_recording = False
        return
    
    resampler = AudioResampler(
        input_rate=YL200S_RATE,
        output_rate=TARGET_RATE,
        input_channels=YL200S_CHANNELS
    )
    
    ws = None
    last_reconnect_time = 0
    reconnect_interval = 0.5
    
    try:
        while is_recording and not stop_recording_event.is_set():
            # WebSocket 连接管理
            if ws is None or not ws.connected:
                current_time = time.time()
                if current_time - last_reconnect_time < reconnect_interval:
                    time.sleep(0.05)
                    continue
                    
                try:
                    if ws:
                        try:
                            ws.close()
                        except:
                            pass
                    
                    ws = create_websocket_connection()
                    send_start_params(ws)
                    last_reconnect_time = current_time
                    logger.info("WebSocket 已连接")
                except Exception as e:
                    logger.error(f"连接失败: {e}")
                    last_reconnect_time = current_time
                    time.sleep(0.1)
                    continue
            
            # 读取并处理音频
            try:
                raw_data = audio_stream.read(YL200S_CHUNK, exception_on_overflow=False)
                
                # 直接重采样发送音频给百度云，不再缓存声纹数据
                resampled_data = resampler.process(raw_data)
                ws.send_binary(resampled_data)
                
            except Exception as e:
                logger.debug(f"发送音频失败: {e}")
                ws = None
                continue
            
            # 接收消息
            try:
                ws.settimeout(0.01)
                while True:
                    try:
                        message = ws.recv()
                        if message:
                            on_message_handler(message)
                    except websocket.WebSocketTimeoutException:
                        break
                    
            except Exception as e:
                logger.debug(f"接收消息失败: {e}")
                ws = None
                
    except Exception as e:
        logger.error(f"录音过程出错: {e}")
    finally:
        # 发送结束帧并关闭连接
        if ws and ws.connected:
            try:
                send_finish(ws)
                ws.close()
            except:
                pass
        
        is_recording = False


def manual_input_mode():
    """手动输入测试模式 - 模拟完整的语音交互流程"""
    global is_wake_up_mode, all_results
    
    print("\n" + "=" * 50)
    print("🖊️  手动输入测试模式 (模拟语音交互)")
    print("=" * 50)
    print("\n📌 使用流程:")
    print("   1. 先输入唤醒词: '考拉一号' 或 '考拉1号'")
    print("   2. 看到提示后，可连续输入不同指令，无需反复唤醒")
    print(f"   3. {IDLE_TIMEOUT}秒不输入或输入'退下'等词会自动休眠")
    print("\n📌 指令格式示例:")
    print("   帮我到吧台拿咖啡")
    print("   走两步看看")
    print("   上海天气怎么样")
    print("\n📌 控制命令:")
    print("   输入 'q' 退出测试模式")
    print("   输入 'r' 强制重置到唤醒监听模式")
    print("=" * 50 + "\n")
    
    is_wake_up_mode = True
    all_results = []
    
    while True:
        try:
            if is_wake_up_mode:
                prompt = "🔊 监听中 (等待唤醒词) > "
            else:
                prompt = "🎤 已唤醒 (请输入指令 或 退下) > "
            
            user_input = input(prompt).strip()
            
            if user_input.lower() == 'q':
                print("退出测试模式")
                break
            
            if user_input.lower() == 'r':
                print("\n🔄 重置到唤醒监听模式")
                enter_sleep_mode()
                continue
            
            if not user_input:
                continue
            
            if is_wake_up_mode:
                wake_words = ["考拉一号", "考拉1号", "考拉壹号", "1号", "一号"]
                is_wake = any(word in user_input for word in wake_words)
                
                if is_wake:
                    # 👇 完美复用真实语音流中的唤醒函数（包含暂停、播报和倒计时重置）
                    trigger_wake_word()
                else:
                    print(f"❌ 未检测到唤醒词: {user_input}")
                    print(f"   请输入包含 '考拉一号' 的语句\n")
            
            else:
                # 👇 拦截主动退下指令
                quit_words = ["退下", "休息吧", "没事了", "拜拜", "再见", "跪安"]
                if any(w in user_input for w in quit_words):
                    print(f"\n📝 收到主动休眠指令: {user_input}")
                    enter_sleep_mode()
                    continue

                print(f"💭 识别结果: {user_input}")
                all_results.append(user_input)
                
                # 放在后台线程去发指令，防止阻塞输入台
                threading.Thread(target=send_keyword_notification, args=(user_input,), daemon=True).start()
                
                # 👇 完成后不重新强制休眠，而是重置发呆倒计时
                print(f"\n⏱️ 指令分析中！测试态活跃时间已重置，可继续敲回车下发新指令...")
                reset_idle_timer()
                print("-" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n退出测试模式")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()



def main():
    """主函数"""
    global is_running, is_recording
    
    print("\n" + "=" * 50)
    print("🎙️  实时语音识别系统 - YL200S麦克风版本")
    print("=" * 50)
    print("\n📌 使用说明:")
    print("   麦克风: YL200S (48kHz 双声道)")
    print("   唤醒词: '考拉 1 号'，然后说出物品和地点")
    print("   物品: 可乐 / 芬达 / 椰子水")
    print("   地点: 吧台 (默认送到 __DEPARTURE__)")
    print("   识别完成后自动回到监听模式")
    print("   按 'q' 退出, 't' 测试, 's' 切换展览模式")
    print("=" * 50 + "\n")
    
    # 启动 WebSocket Server
    server_thread = threading.Thread(target=lambda: asyncio.run(websocket_server()), daemon=True)
    server_thread.start()
    
    # 启动录音监听
    threading.Thread(target=record_and_recognize, daemon=True).start()
    
    # 设置终端为原始模式
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
    
    print("🔊 正在监听唤醒词 '考拉 1 号'... 按 'q' 退出, 't' 测试")
    
    try:
        while is_running:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1).strip().lower()
                if key == 'q':
                    print("\n👋 退出程序...")
                    is_running = False
                    stop_recording_event.set()
                    break
                elif key == 't':
                    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
                    manual_input_mode()
                    tty.setraw(sys.stdin.fileno())
                    print("\n🔊 回到监听模式... 按 'q' 退出, 't' 测试" ,'s' "展览")
                elif key == 's':
                    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
                    toggle_exhibition_mode()
                    tty.setraw(sys.stdin.fileno())
    except KeyboardInterrupt:
        print("\n\n⚠️  程序已停止")
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        close_audio()
        print("\n程序已退出")


if __name__ == "__main__":
    logging.basicConfig(
        format='[%(asctime)-15s] [%(funcName)s()][%(levelname)s] %(message)s',
        level=logging.WARNING,
        filename='server_yl200s.log',
        filemode='a'
    )
    
    main()