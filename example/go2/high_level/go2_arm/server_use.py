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

os.environ['ALSA_CARD'] = '0'
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
        
        # 优先查找 4-mic Microphone
        for line in lines:
            if '4-mic_Microphone' in line or 'alsa_input.usb-rockchip' in line:
                parts = line.split()
                if len(parts) >= 2:
                    device_name = parts[1]
                    logger.info(f"找到 4-mic 麦克风: {device_name}")
                    return device_name
        
        # 如果没找到，返回第一个非 monitor 的输入设备
        for line in lines:
            if 'alsa_input' in line and 'monitor' not in line:
                parts = line.split()
                if len(parts) >= 2:
                    device_name = parts[1]
                    logger.info(f"找到输入设备: {device_name}")
                    return device_name

        logger.warning("未找到麦克风设备")
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
        if '4-mic' in info['name'] or 'rockchip' in info['name'].lower():
            logger.info(f"使用 4-mic 麦克风 (索引: {i})")
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
            "vad_silence_time": 500, 
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
    global is_buffering_for_voiceprint
    
    try:
        msg_data = json.loads(message)
        msg_type = msg_data.get("type")
        
        if msg_type == "MID_TEXT":
            result = msg_data.get("result", "")
            last_mid_text_time = time.time()
            last_mid_text_content = result
            
            if is_wake_up_mode:
                print(f"\r🔊 监听中: {result}    ", end="", flush=True)
                
                # 检测到可能的唤醒词时，开始缓存音频
                if not is_buffering_for_voiceprint:
                    is_buffering_for_voiceprint = True
                    print(f"\n   📝 开始缓存音频用于声纹识别...", end="", flush=True)
                
                # 检测完整唤醒词
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
                        if "1 号" in final_result or "一号" in final_result or "壹号" in final_result or "1号" in final_result or "考拉" in final_result:
                            print(f"\n🎉 检测到唤醒词 (FIN_TEXT): {final_result}")
                            trigger_wake_word()
                        else:
                            print(f"\n❌ 未检测到唤醒词: {final_result}")
                            # 重置缓存
                            wake_audio_buffer.clear()
                            is_buffering_for_voiceprint = False
                    else:
                        all_results.append(final_result)
                        print(f"\n📝 片段结果: {final_result}")
                        send_keyword_notification(final_result)
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
    """触发唤醒词的通用函数（增强版：集成声纹识别）"""
    global is_wake_up_mode, all_results, wake_audio_buffer, is_buffering_for_voiceprint
    
    if not is_wake_up_mode:
        return
    
    print("\n" + "=" * 60)
    print("🎉 检测到唤醒词！")
    print("=" * 60)
    
    # 1. 暂停机器人运动
    print("⏸️  暂停运动，准备识别关键词...")
    pause_command = (
        "source /opt/ros/noetic/setup.bash && "
        'rostopic pub /neupan/pause std_msgs/Empty "{}" -1'
    )
    
    try:
        result = subprocess.run(
            pause_command,
            shell=True,
            executable='/bin/bash',
            capture_output=True,
            timeout=3,
            text=True
        )
        print("✓ 暂停运动命令已发送")
    except Exception as e:
        print(f"❌ 发送暂停命令失败: {e}")
    
    # 2. 声纹识别
    recognized_speaker = None
    recognition_score = 0
    
    if wake_audio_buffer:
        print(f"\n🔍 正在进行声纹识别... (缓存音频: {len(wake_audio_buffer)} 帧)")
        
        # 合并缓存的音频数据
        combined_audio = b''.join(wake_audio_buffer)
        
        # 执行声纹识别
        recognized_speaker, recognition_score = perform_voiceprint_recognition(combined_audio)
        
        if recognized_speaker:
            speaker_info = VOICE_RECOGNITION_CONFIG["known_speakers"].get(
                recognized_speaker,
                {"name": recognized_speaker, "audio_file": None}
            )
            print(f"\n✅ 识别到说话人: {speaker_info['name']} (置信度: {recognition_score:.2%})")
        else:
            print(f"\n⚠️ 未能确认说话人身份 (最高相似度: {recognition_score:.2%})")
    else:
        print("\n⚠️ 没有缓存的音频数据，跳过声纹识别")
    
    # 3. 根据声纹识别结果播放不同音频
    audio_file = None
    
    if recognized_speaker and recognized_speaker in VOICE_RECOGNITION_CONFIG["known_speakers"]:
        # 播放个性化问候
        speaker_config = VOICE_RECOGNITION_CONFIG["known_speakers"][recognized_speaker]
        audio_file = speaker_config.get("audio_file")
        if audio_file and os.path.exists(audio_file):
            print(f"🔊 播放专属问候: {os.path.basename(audio_file)}")
        else:
            print(f"⚠️ 专属音频不存在: {audio_file}")
            audio_file = "/home/unitree/dky/go2_python_sdk2/data/wav_files/start_listening.wav"
    else:
        # 播放默认提示音
        audio_file = "/home/unitree/dky/go2_python_sdk2/data/wav_files/start_listening.wav"
        print(f"🔊 播放默认提示音: {os.path.basename(audio_file)}")
    
    try:
        if audio_file:
            threading.Thread(target=play_audio, args=(audio_file,), daemon=True).start()
    except Exception as e:
        logger.warning(f"播放唤醒音失败: {e}")
    
    # 4. 切换到识别模式
    print("\n🔄 切换到识别模式，等待指令...")
    print("=" * 60 + "\n")
    
    is_wake_up_mode = False
    all_results = []
    
    # 重置音频缓存
    wake_audio_buffer = []
    is_buffering_for_voiceprint = False


def extract_keywords(text):
    """从文本中提取物品和地点关键词"""
    result = []
    
    detected_item_name = None
    for item in items:
        if item in text:
            detected_item_name = item
            print(f"→ 检测到物品: {item}")
            break
    
    if detected_item_name is None:
        print(f"⚠️ 未检测到有效物品关键词")
        return None, None, None
    
    result.append(detected_item_name)
    
    delivery_keywords = ["送到", "送给", "送至", "带到"]
    delivery_index = -1
    delivery_keyword_found = None
    
    for keyword in delivery_keywords:
        if keyword in text:
            delivery_index = text.find(keyword)
            delivery_keyword_found = keyword
            print(f"→ 检测到送达关键词: '{keyword}' (位置: {delivery_index})")
            break
    
    detected_positions = []
    for position in positions:
        if position in text:
            index = text.find(position)
            detected_positions.append((index, position))
            print(f"→ 检测到地点: {position} (位置: {index})")
    
    detected_positions.sort(key=lambda x: x[0])
    
    delivery_location = None
    if delivery_index != -1:
        for pos_index, position in detected_positions:
            if pos_index > delivery_index:
                delivery_location = position
                print(f"✓ 确定送达地点: {position}")
                break
    
    for _, position in detected_positions:
        result.append(position)
    
    if len(result) == 1:
        print(f"⚠️ 只检测到物品，未检测到地点")
    
    return result, detected_item_name, delivery_location


def send_keyword_notification(final_result):
    """检测关键词并发送到客户端"""
    keywords, item_name, delivery_location = extract_keywords(final_result)
    
    if keywords is None:
        print("❌ 未检测到有效关键词组合，不发送消息")
        return
    
    if len(keywords) < 2:
        print("❌ 没有检测到地点，不发送消息")
        print("   请说出完整的指令，例如：'去前台拿水送到办公室'")
        return
    
    message_data = {
        "item": keywords[0],
        "locations": keywords[1:] if len(keywords) > 1 else [],
        "delivery_location": delivery_location
    }
    
    message_json = json.dumps(message_data, ensure_ascii=False)
    
    print(f"\n📤 发送到客户端:")
    print(f"   物品: {keywords[0]}")
    if len(keywords) > 1:
        print(f"   地点列表: {keywords[1:]}")
    else:
        print(f"   地点列表: 无")
    if delivery_location:
        print(f"   送达地点: {delivery_location} ⭐")
    print(f"   JSON数据: {message_json}\n")
    
    audio_file_map = {
        "水": "/home/unitree/dky/go2_python_sdk2/data/wav_files/water_start.wav",
        "纸": "/home/unitree/dky/go2_python_sdk2/data/wav_files/tissue_start.wav",
        "糖": "/home/unitree/dky/go2_python_sdk2/data/wav_files/sugar_start.wav",
        "咖啡": "/home/unitree/dky/go2_python_sdk2/data/wav_files/coffee_start.wav",
        "雨伞": "/home/unitree/dky/go2_python_sdk2/data/wav_files/umbrella_start.wav",
        "外卖": "/home/unitree/dky/go2_python_sdk2/data/wav_files/takeout_start.wav",
        "饮料": "/home/unitree/dky/go2_python_sdk2/data/wav_files/yinliao_start.wav",
    }
    
    if item_name in audio_file_map:
        try:
            audio_file = audio_file_map[item_name]
            threading.Thread(target=play_audio, args=(audio_file,), daemon=True).start()
            print(f"🔊 已触发播放 {os.path.basename(audio_file)}")
        except Exception as e:
            logger.warning(f"播放音频失败: {e}")
    
    message_queue.put(message_json)


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
    global wake_audio_buffer, is_buffering_for_voiceprint
    
    all_results = []
    is_recording = True
    stop_recording_event.clear()
    wake_audio_buffer = []
    is_buffering_for_voiceprint = True

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
                
                # 在唤醒监听模式时缓存原始音频用于声纹识别
                if is_wake_up_mode:
                    save_audio_for_voiceprint(raw_data)
                
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
                    
                    print("暂停运动，准备识别关键词...")
                    pause_command = (
                        "source /opt/ros/noetic/setup.bash && "
                        'rostopic pub /neupan/pause std_msgs/Empty "{}" -1'
                    )
                    
                    try:
                        result = subprocess.run(
                            pause_command,
                            shell=True,
                            executable='/bin/bash',
                            capture_output=True,
                            timeout=10,
                            text=True
                        )
                        if result.returncode == 0:
                            print("✓ 暂停运动命令已发送")
                        else:
                            print(f"⚠️ 暂停命令返回错误: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        print("⚠️ rostopic pub 超时")
                    except Exception as e:
                        print(f"❌ 发送暂停命令失败: {e}")
                    
                    try:
                        audio_file = "/home/unitree/dky/go2_python_sdk2/data/wav_files/start_listening.wav"
                        print(f"🔊 播放提示音: {os.path.basename(audio_file)}")
                        threading.Thread(target=play_audio, args=(audio_file,), daemon=True).start()
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