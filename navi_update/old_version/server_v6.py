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
# 👇 引入 TTS 模块并初始化
from tts import speak_with_cherry, init_dashscope_api_key
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

positions = ["前台", "办公室", "吧台", "初始位置","门口","雨伞架"]
items = ["水", "纸", "糖", "咖啡", "雨伞","外卖","饮料"]

ITEM_DEFAULT_LOCATION = {
    "雨伞": "雨伞架",    # 雨伞默认从雨伞架取
    "外卖": "门口",      # 外卖默认从门口取
    "水": "吧台",        # 水默认从吧台取
    "咖啡": "吧台",      # 咖啡默认从吧台取
    "饮料": "吧台",      # 饮料默认从吧台取
    # 可以继续添加其他物品的默认地点
}
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
                        all_results.append(final_result)
                        print(f"\n📝 片段结果: {final_result}")
                        threading.Thread(target=send_keyword_notification, args=(final_result,), daemon=True).start()
                        print("🔄 识别完成，回到唤醒监听模式...")
                        is_wake_up_mode = True
            
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
    print("🎉 检测到唤醒词！")
    print("=" * 60)
    
    print("⏸️  暂停运动，准备识别关键词...")
    try:
        message_queue.put("pause")
        print("✓ 暂停命令已发送到客户端")
    except Exception as e:
        print(f"❌ 发送暂停命令失败: {e}")
    
    # 取消声纹，统一使用普通回复
    greeting = "考拉来啦！"
    print(f"🔊 播放提示音: {greeting}")
    try:
        threading.Thread(target=speak_with_cherry, args=(greeting,), daemon=True).start()
    except Exception as e:
        logger.warning(f"播放唤醒音失败: {e}")
    
    # 切换到识别模式
    print("\n🔄 切换到识别模式，等待指令...")
    print("=" * 60 + "\n")
    
    is_wake_up_mode = False
    all_results = []

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

# 👇 新增：系统模式全局变量
current_system_mode = "表演模式"  # 默认启动时为跑腿模式

# 👇 修改：分离两种模式的神级提示词 (Prompts)
LLM_PROMPT_NAV = """你是一只考拉，当前处于【跑腿取物模式】。
必须将任务翻译成一个精确且按顺序排列的原子动作列表(action_plan)。
支持的原子 action 有：
- "navigate": 导航，必须包含 "location" 字段（前台/办公室/吧台/门口/雨伞架/__DEPARTURE__）。
- "squat": 蹲下，可包含 "location" 协助判断姿势。
- "send_grasp_msg": 通知机械臂抓取，必须包含 "item" 字段。
- "wait_for_back": 等待机械臂完成。
- "stand_up": 站立。
- "release_item": 放下物品（送达时用于向机械臂发送释放指令）。
- "wait_for_play": 等待放下动作完成（必须接在 release_item 之后）。
- "play_audio": 播放完成提示音。

只输出 JSON 格式，且包含 action_plan 和 item（若有物品）。
item 字段必须是用户指令中明确提到的物品（如可乐，芬达，椰子水，水 等），如果没有明确物品则返回 "none"。
👇【重要】输出示例必须严格遵循完整的流水线顺序：
示例2（未说明送达地）："去帮我去吧台拿瓶可乐"
输出：{"item": "可乐", "action_plan": [{"action": "stand_up"}, {"action": "navigate", "location": "吧台"}, {"action": "squat"}, {"action": "send_grasp_msg", "item": "可乐"}, {"action": "wait_for_back"}, {"action": "stand_up"}, {"action": "navigate", "location": "__DEPARTURE__"}, {"action": "squat"}, {"action": "release_item"}, {"action": "wait_for_play"}, {"action": "play_audio"}]}

说明：
1. 包含抓取要求时，必须严格执行【📌出发前先站立(stand_up) -> 导航至取物点 -> 蹲下 -> 要求抓取 -> 等待 -> 站立(stand_up) -> 导航至送达点 -> 📌到达后先蹲下(squat) -> 放下物品(release_item) -> 等待放稳(wait_for_play) -> 播放音效】的绝对顺序！
2. 📌 默认返回归位：如果用户的指令里只有“去哪拿什么”，而没有明确说送到哪里，那么拿到物品后，最后一次的 navigate 的 location 必须写 "__DEPARTURE__"。



⚠️【重要容错规则】：
如果用户的指令纯粹是让你表演动作（如走两步、站起、趴下、打招呼）或者闲聊找你玩，这超出了跑腿模式职责！
请立刻停止规划，直接输出如下JSON以报错返回：
{"error": "mode_mismatch", "item": "none", "action_plan": []}
"""

LLM_PROMPT_PERF = """你是一只聪明可爱的考拉，当前处于【表演与聊天模式】。
用户会和你聊天，或者让你表演一些动作。

【核心要求】：
1. "chat_reply" 的回复必须要简短、口语化，像跟朋友闲聊一样。
2. 绝对不能出现任何小括号及括号里的动作描写词（如“笑”、“晃动”等）。
3. 必须返回 JSON 格式，包含 "chat_reply"、"action_plan" 两个字段。
4. ⚠️ 严格区分闲聊与动作：
   - 纯聊天不输出动作，action_plan 必须为空列表 []。
   - 仅在明确要求做动作时才在 action_plan 加入原子动作。

支持选用的原子 action 有：
- "hello": 打招呼
- "rotate": 旋转 
- "lie_down": 趴下
- "stand_up": 站立
- "stretch": 伸懒腰
- "walk_forward": 向前走
- "walk_backward": 向后走
- "walk_left":  向左移动
- "walk_right": 向右移动

【输出示例】：
- 闲聊情景：用户输入“晚上吃什么？” 
  输出: {"chat_reply": "不如去吃好吃的水果吧！", "action_plan": []}
- 动作情景1：用户输入“给大家打个招呼” 
  输出: {"chat_reply": "大家好呀，很高兴见到你们！", "action_plan": [{"action": "hello"}]}
- 动作情景2：用户输入“向前走两步看看” 
  输出: {"chat_reply": "好嘞，看我的！", "action_plan": [{"action": "walk_forward"}]}


⚠️【重要容错规则】：
如果用户要求你去某个地点跑腿拿东西（如去吧台拿水、跨房间送物），这超出了表演模式的职责！
请立刻停止规划，直接输出如下JSON以报错返回：
{"error": "mode_mismatch", "chat_reply": "none", "action_plan": []}
"""

def parse_with_llm(text):
    """使用大模型解析自然语言并直接生成执行规划"""
    global current_system_mode
    print(f"\n🤖 规划大脑思考中 [{current_system_mode}]: '{text}'")
    
    # 根据当前模式挂载对应的系统脑印
    prompt = LLM_PROMPT_NAV if current_system_mode == "跑腿模式" else LLM_PROMPT_PERF
    
    try:
        response = llm_client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=250,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content.strip()
        print(f"   📥 规划方案:\n{content}")
        return json.loads(content)
    
    except Exception as e:
        print(f"❌ 规划失败: {e}")
        return None

def classify_mode_with_llm(text):
    """用 LLM 智能判断用户的纯粹 '切换状态' 意图"""
    try:
        system_prompt = """你是一个意图分类器。你要判断用户是在【泛泛地请求切换模式】，还是在【下达具体的任务指令】。

规则如下：
1. 切换到娱乐/休息（仅输出 PERF）：如“咱们聊聊天”、“我想看表演”、“我要切换表演模式”。注意：不能包含具体的动作名。
2. 切换到跑腿/干活（仅输出 NAV）：如“我要你帮我取个东西”、“准备干活了”、“跑腿模式”。注意：不能包含具体的地点或物品名。
3. 具体的跑腿任务或表演闲聊（仅输出 NONE）：
   ⚠️ 铁律：只要句子中出现了具体的【地点】（如吧台、前台、办公室、门口等）或明确的【物品】（如饮料、水、外卖、雨伞、咖啡等），说明用户已经在下达真实的业务指令了！不管有没有“帮我”字眼，都必须当场输出 NONE！
   示例1：“你去吧台帮我拿瓶饮料吧！” -> 包含地点(吧台)和物品(饮料)，必须输出 NONE。
   示例2：“帮我去前台拿个外卖” -> 必须输出 NONE。
   示例3：“走两步” -> 具体的动作指令，输出 NONE。

请严格判定，只输出 PERF, NAV 或 NONE 三个单词之一。"""

        resp = llm_client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=8
        )
        content = resp.choices[0].message.content.strip().upper()
        if "PERF" in content:
            return "PERF"
        if "NAV" in content:
            return "NAV"
        return "NONE"
    except Exception as e:
        print(f"⚠️ 状态分类网络异常，默认无视切换: {e}")
        return "NONE"

def send_keyword_notification(final_result):
    global current_system_mode
    
    # ================= 纯血 LLM 模式切换路由 =================
    mode = classify_mode_with_llm(final_result)
    
    if mode == "PERF":
        # 只有当前不是表演模式时，才属于真正的"切换状态"，切完播报并拉断。
        if current_system_mode != "表演模式":
            current_system_mode = "表演模式"
            print("\n🔄 状态路由判定：切换至 🎭 表演模式")
            threading.Thread(target=speak_with_cherry, args=("我准备好跟你玩儿啦！",), daemon=True).start()
            return  
        # 👇 如果已经是表演模式，说明是一句顺势的闲聊（例如：做个自我介绍吧），直接放行给大脑！

    elif mode == "NAV":
        if current_system_mode != "跑腿模式":
            current_system_mode = "跑腿模式"
            print("\n🔄 状态路由判定：切换至 🚀 跑腿模式")
            threading.Thread(target=speak_with_cherry, args=("我准备好帮你拿东西啦！",), daemon=True).start()
            return  
    # =========================================================

    # 只有判定为 NONE (即带有实际目的的句子)，才会走到具体的解析网络
    llm_result = parse_with_llm(final_result)
    
    if isinstance(llm_result, list):
        llm_result = {"action_plan": llm_result}
        
    if not llm_result:
        print("❌ 解析数据异常或规划失败")
        return

    if "action_plan" in llm_result:
        clean_plan = []
        for step in llm_result["action_plan"]:
            if isinstance(step, str):
                clean_plan.append({"action": step})
            elif isinstance(step, dict):
                clean_plan.append(step)
        llm_result["action_plan"] = clean_plan
        
    if current_system_mode == "跑腿模式":
        if llm_result.get("error") == "mode_mismatch":
            # 👇 同步更新下大模型的拒绝提示音
            warn_text = "如果想看表演，您可以对我说：我想跟你玩会儿。"
            print(f"⚠️ 越界指令被拦截：提醒切换模式")
            threading.Thread(target=speak_with_cherry, args=(warn_text,), daemon=True).start()
            return
            
        if "action_plan" in llm_result:
            message_json = json.dumps(llm_result, ensure_ascii=False)
            print(f"\n📤 下发[导航]执行指令:\n{message_json}\n")
            
            item_name = llm_result.get("item", "物品")
            text_to_speak = f"好的，马上去帮您拿{item_name}。"
            
            def speak_then_send_nav():
                try:
                    print(f"🔊 播放提示音: {text_to_speak}")
                    speak_with_cherry(text_to_speak)
                finally:
                    message_queue.put(message_json)
            threading.Thread(target=speak_then_send_nav, daemon=True).start()
        else:
            print("❌ 数据格式不支持导航分配")

    elif current_system_mode == "表演模式":
        if llm_result.get("error") == "mode_mismatch":
            # 👇 同步更新下大模型的拒绝提示音 (同时加上防掐断后缀)
            warn_text = "如果要我跑腿拿东西，您可以对我说：我想让你帮我取个东西。..."
            print(f"⚠️ 越界指令被拦截：提醒切换模式")
            threading.Thread(target=speak_with_cherry, args=(warn_text,), daemon=True).start()
            return
            
        chat_text = llm_result.get("chat_reply", "收到啦！")
        if not chat_text.endswith("..."):
            chat_text += "..."  # 自动加上尾音防截断
            
        action_plan = llm_result.get("action_plan", [])
    
        
        if action_plan:
            message_json = json.dumps({"action_plan": action_plan}, ensure_ascii=False)
             
            # 获取里面所有的具体原子动作名称
            action_types = [step.get("action") for step in action_plan if isinstance(step, dict)]
            
            if any(a in action_types for a in ["walk", "rotate"]):
                def speak_then_action():
                    try:
                        print(f"🎤 聊天回复 [策略：先说后做]: {chat_text}")
                        speak_with_cherry(chat_text)
                    finally:
                        print(f"\n📤 语音已播放完毕，正式下发动作:\n{message_json}\n")
                        message_queue.put(message_json)
                threading.Thread(target=speak_then_action, daemon=True).start()
                
            elif any(a in action_types for a in ["hello"]):
                def action_then_speak():
                    # 1. 毫不犹豫在一瞬间下发指令，让机械狗立刻开始跑 Conda 的底层耗时
                    print(f"\n📤 捕捉到同步动作，立刻下发指令 (拉起物理端):\n{message_json}\n")
                    message_queue.put(message_json)
                    
                    # 2. Server 语音心脏开始静默等待，给机械预留举手的反应时间
                    print("⏳ 物理环境启动中，等待 10 秒以卡对音画同频点...")
                    time.sleep(8.0)
                    
                    # 3. 时间到，狗举手，扬声器卡点发声
                    print(f"🎤 聊天回复 [策略：卡点同步]: {chat_text}")
                    speak_with_cherry(chat_text)
                threading.Thread(target=action_then_speak, daemon=True).start()
            else:
                # 兜底：其它无指定动作，边说边做
                message_queue.put(message_json)
                threading.Thread(target=speak_with_cherry, args=(chat_text,), daemon=True).start()
                
                
        else:
            print("✅ 纯闲聊，无额外动作指令。")
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
    print("   2. 看到提示后，输入完整指令")
    print("   3. 系统识别关键词并发送消息")
    print("\n📌 指令格式示例:")
    print("   帮我到吧台拿咖啡送到办公室回到初始位置")
    print("   去前台拿红色雨伞送到办公室")
    print("   去办公室拿糖送到初始位置")
    print("\n📌 控制命令:")
    print("   输入 'q' 退出测试模式")
    print("   输入 'r' 重置到唤醒监听模式")
    print("=" * 50 + "\n")
    
    is_wake_up_mode = True
    all_results = []
    
    while True:
        try:
            if is_wake_up_mode:
                prompt = "🔊 监听中 (等待唤醒词) > "
            else:
                prompt = "🎤 识别中 (请输入指令) > "
            
            user_input = input(prompt).strip()
            
            if user_input.lower() == 'q':
                print("退出测试模式")
                break
            
            if user_input.lower() == 'r':
                print("\n🔄 重置到唤醒监听模式")
                is_wake_up_mode = True
                all_results = []
                continue
            
            if not user_input:
                continue
            
            if is_wake_up_mode:
                wake_words = ["考拉一号", "考拉1号", "考拉壹号", "1号", "一号"]
                is_wake = any(word in user_input for word in wake_words)
                
                if is_wake:
                    print(f"\n🎉 检测到唤醒词: {user_input}")
                    
                    # 👇 修改：通过 WebSocket 发送 pause 消息给 client
                    print("暂停运动，准备识别关键词...")
                    try:
                        message_queue.put("pause")
                        print("✓ 暂停命令已发送到客户端")
                    except Exception as e:
                        print(f"❌ 发送暂停命令失败: {e}")
                    
                    try:
                        greeting = "考拉来啦！"
                        print(f"🔊 播放提示音: {greeting}")
                        threading.Thread(target=speak_with_cherry, args=(greeting,), daemon=True).start()
                    except Exception as e:
                        print(f"❌ 播放提示音失败: {e}")
                    
                    print("🔄 切换到识别模式...")
                    is_wake_up_mode = False
                    all_results = []
                    print()
                else:
                    print(f"❌ 未检测到唤醒词: {user_input}")
                    print(f"   请输入包含 '考拉一号' 的语句\n")
            
            else:
                print(f"💭 识别结果: {user_input}")
                all_results.append(user_input)
                
                print()
                send_keyword_notification(user_input)
                
                print("\n🔄 识别完成，回到唤醒监听模式...")
                is_wake_up_mode = True
                all_results = []
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
    print("   物品: 水 / 纸 / 糖 / 咖啡 / 雨伞")
    print("   地点: 前台 / 办公室 / 吧台 / 起始位置")
    print("   示例: '去帮我到前台拿水送到办公室'")
    print("   识别完成后自动回到监听模式")
    print("   按 'q' 退出程序, 't' 测试模式")
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
                    print("\n🔊 回到监听模式... 按 'q' 退出, 't' 测试")
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