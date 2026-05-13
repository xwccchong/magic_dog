#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦克风录音 + 语音识别 多进程模块

架构 (参考 mp_single_realsense / mp_robot_state):
- 子进程: 独立 mp.Process, 持续从 DJI 麦克风采集音频,
           重采样后流式发送百度云 WebSocket 进行实时识别
- 主进程: 通过 mp.Queue 接收识别结果事件
- 共享内存: 写入状态供 mp_show_info 监控

与 server_recon_v3.py (单进程多线程版) 的区别:
  - 录音 + 识别完全隔离在子进程, 不阻塞主进程 GIL
  - LLM 解析 / TTS 播放 / 展览模式等逻辑留在主进程
  - 使用 multiprocessing.Queue 传递事件, 进程隔离更稳定
  - 使用共享内存写入状态, 跨进程可读取

用法:
    audio = AudioRecordSubProcess(
        audio_config={...},
        baidu_config={...},
        recognition_config={...},
        enable_status=True,  # 启用共享内存状态
    )
    audio.start()

    while True:
        result = audio.get_result(timeout=5.0)
        if result:
            # 处理识别结果

    audio.stop()
"""

import os
import time
import json
import uuid
import logging
import subprocess
import multiprocessing as mp
import threading
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

# 导入共享内存模块
try:
    from shared_memory_buffer import SharedMemoryArray
except ImportError:
    SharedMemoryArray = None


# ======================================================================
# 子进程入口: 麦克风录音 + 百度云语音识别
# ======================================================================
def _audio_worker(
    result_queue: mp.Queue,
    command_queue: mp.Queue,
    stop_event: mp.Event,
    ready_event: mp.Event,
    error_queue: mp.Queue,
    audio_config: dict,
    baidu_config: dict,
    recognition_config: dict,
    status_shm_name: str = None,
):
    """
    子进程入口函数: 持续录音 + 百度云语音识别

    Args:
        result_queue:  主进程 <- 子进程 (识别结果事件)
        command_queue: 主进程 -> 子进程 (控制命令)
        stop_event:    停止信号
        ready_event:   就绪信号
        error_queue:   错误上报
        audio_config:  音频参数 {chunk, channels, rate, target_channels, target_rate}
        baidu_config:  百度参数 {appid, appkey, dev_pid, uri}
        recognition_config: 识别参数 {vad_silence_time, idle_timeout, wake_words, quit_words}
        status_shm_name: 状态共享内存名称 (用于 mp_show_info 监控)
    """
    # ---- 子进程内延迟导入, 避免主进程依赖 ----
    import pyaudio
    import websocket
    from scipy import signal as scipy_signal

    # ---- 解包配置 ----
    CHUNK = audio_config.get('chunk', 1024)
    CHANNELS = audio_config.get('channels', 2)
    RATE = audio_config.get('rate', 48000)
    TARGET_RATE = audio_config.get('target_rate', 16000)
    _ = audio_config.get('target_channels', 1)
    FORMAT = pyaudio.paInt16

    BAIDU_APPID = baidu_config.get('appid', '')
    BAIDU_APPKEY = baidu_config.get('appkey', '')
    BAIDU_DEV_PID = baidu_config.get('dev_pid', 1537)
    BAIDU_URI = baidu_config.get('uri', '')

    VAD_SILENCE_TIME = recognition_config.get('vad_silence_time', 1500)
    IDLE_TIMEOUT = recognition_config.get('idle_timeout', 500.0)
    WAKE_WORDS = recognition_config.get('wake_words', ['考拉一号', '考拉1号'])
    QUIT_WORDS = recognition_config.get('quit_words', ['退下', '休息', '下去吧'])

    # ---- 内部状态 ----
    pyaudio_instance = None
    audio_stream = None
    is_wake_up_mode = True
    idle_timer = None
    last_mid_text_time = 0

    # ---- 共享内存状态 ----
    # 布局: [is_ready, is_running, error_flag, padding, ..., last_update]
    status_arr = None
    if status_shm_name and SharedMemoryArray is not None:
        try:
            status_arr = SharedMemoryArray.connect(
                name=status_shm_name,
                shape=(8,),
                dtype=np.float64,
            )
            logger.info(f"[Audio-SubProcess] 已连接状态共享内存: {status_shm_name}")
        except Exception as e:
            logger.warning(f"[Audio-SubProcess] 无法连接状态共享内存: {e}")

    def update_status(is_ready=None, is_running=None, error_flag=None, message=None):
        """更新共享内存状态"""
        if status_arr is None:
            return
        try:
            data, seq = status_arr.read()
            if is_ready is not None:
                data[0] = 1.0 if is_ready else 0.0
            if is_running is not None:
                data[1] = 1.0 if is_running else 0.0
            if error_flag is not None:
                data[2] = 1.0 if error_flag else 0.0
            if message is not None:
                # 消息存储在额外位置，这里只更新最后更新时间
                pass
            data[7] = time.time()  # last_update
            status_arr.write(data)
        except Exception as e:
            logger.debug(f"[Audio-SubProcess] 状态更新失败: {e}")

    def set_status_error(error_msg: str):
        """设置错误状态"""
        update_status(error_flag=True, message=error_msg)

    def clear_status_error():
        """清除错误状态"""
        update_status(error_flag=False)

    # ================================================================
    # 音频重采样器: 双声道 48kHz -> 单声道 16kHz
    # ================================================================
    class AudioResampler:
        def __init__(self, input_rate, output_rate, input_channels):
            self.input_rate = input_rate
            self.output_rate = output_rate
            self.input_channels = input_channels
            self.resample_ratio = output_rate / input_rate
            nyquist = output_rate / 2
            cutoff = nyquist * 0.9
            self.sos = scipy_signal.butter(
                8, cutoff, btype='low', fs=input_rate, output='sos'
            )
            self.residual = np.array([], dtype=np.int16)

        def process(self, audio_data):
            """处理音频: 双声道->单声道, 48kHz->16kHz"""
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            if self.input_channels == 2:
                audio_np = audio_np.reshape(-1, 2)
                audio_mono = audio_np.mean(axis=1).astype(np.int16)
            else:
                audio_mono = audio_np

            if len(self.residual) > 0:
                audio_mono = np.concatenate([self.residual, audio_mono])

            audio_filtered = scipy_signal.sosfilt(
                self.sos, audio_mono.astype(np.float32)
            )
            num_samples = int(len(audio_filtered) * self.resample_ratio)
            audio_resampled = scipy_signal.resample(audio_filtered, num_samples)
            audio_resampled = np.clip(
                audio_resampled, -32768, 32767
            ).astype(np.int16)

            expected_input_samples = int(num_samples / self.resample_ratio)
            self.residual = audio_mono[expected_input_samples:]
            return audio_resampled.tobytes()

    # ================================================================
    # 音频设备管理
    # ================================================================
    def find_yl200s_source():
        """查找 DJI 麦克风 PulseAudio 源"""
        try:
            result = subprocess.run(
                ['pactl', 'list', 'sources', 'short'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return None
            for line in result.stdout.split('\n'):
                if 'DJI_MIC_MINI' in line or 'DJI_Technology' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
            return None
        except Exception:
            return None

    def set_default_source():
        """设置 DJI 为默认 PulseAudio 输入源"""
        try:
            device_name = find_yl200s_source()
            if device_name:
                subprocess.run(
                    ['pactl', 'set-default-source', device_name],
                    check=True, timeout=2
                )
                subprocess.run(
                    ['pactl', 'set-source-mute', device_name, '0'],
                    check=True, timeout=2
                )
            return True
        except Exception:
            return False

    def find_pulse_device(p):
        """查找 PulseAudio 设备索引"""
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['name'] == 'pulse' and info['maxInputChannels'] > 0:
                return i
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if 'DJI Mic MINI' in info['name']:
                return i
        return None

    def init_audio():
        """初始化 DJI 音频设备"""
        nonlocal pyaudio_instance, audio_stream
        set_default_source()
        if pyaudio_instance is None:
            pyaudio_instance = pyaudio.PyAudio()
        if audio_stream is None or not audio_stream.is_active():
            device_index = find_pulse_device(pyaudio_instance)
            if device_index is None:
                raise RuntimeError("未找到音频输入设备")
            audio_stream = pyaudio_instance.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK,
            )
            logger.info(
                f"[Audio-SubProcess] DJI 麦克风已初始化 "
                f"({RATE}Hz, {CHANNELS}ch)"
            )

    def close_audio():
        """关闭音频设备"""
        nonlocal audio_stream, pyaudio_instance
        if audio_stream:
            try:
                audio_stream.stop_stream()
                audio_stream.close()
            except Exception:
                pass
            audio_stream = None
        if pyaudio_instance:
            try:
                pyaudio_instance.terminate()
            except Exception:
                pass
            pyaudio_instance = None

    # ================================================================
    # 百度 WebSocket 通信
    # ================================================================
    def create_ws():
        """创建百度 WebSocket 连接"""
        uri = BAIDU_URI + "?sn=" + str(uuid.uuid1())
        ws = websocket.WebSocket()
        ws.connect(uri)
        return ws

    def send_start(ws):
        """发送开始参数帧"""
        req = {
            "type": "START",
            "data": {
                "appid": BAIDU_APPID,
                "appkey": BAIDU_APPKEY,
                "dev_pid": BAIDU_DEV_PID,
                "cuid": "yl200s_subprocess",
                "sample": TARGET_RATE,
                "format": "pcm",
                "vad_silence_time": VAD_SILENCE_TIME,
            }
        }
        ws.send(json.dumps(req), websocket.ABNF.OPCODE_TEXT)

    def send_finish(ws):
        """发送结束帧"""
        req = {"type": "FINISH"}
        ws.send(json.dumps(req), websocket.ABNF.OPCODE_TEXT)
        logger.info("send FINISH frame")

    # ================================================================
    # 空闲计时器
    # ================================================================
    def reset_idle_timer():
        """每次收到有效对话后, 重置休眠倒计时"""
        nonlocal idle_timer
        if idle_timer:
            idle_timer.cancel()
        idle_timer = threading.Timer(IDLE_TIMEOUT, _on_idle_timeout)
        idle_timer.daemon = True
        idle_timer.start()

    def _on_idle_timeout():
        """空闲超时, 通知主进程进入休眠"""
        nonlocal is_wake_up_mode
        if not is_wake_up_mode:
            is_wake_up_mode = True
            update_status(message="等待唤醒词...")
            result_queue.put({"type": "sleep", "reason": "idle_timeout"})

    # ================================================================
    # 百度消息处理
    # ================================================================
    def on_message(message):
        """
        处理百度 WebSocket 返回的消息
        """
        nonlocal is_wake_up_mode, last_mid_text_time

        try:
            msg = json.loads(message)
            msg_type = msg.get("type")

            if msg_type == "MID_TEXT":
                result = msg.get("result", "")
                last_mid_text_time = time.time()

                if is_wake_up_mode:
                    if result and any(w in result for w in WAKE_WORDS):
                        is_wake_up_mode = False
                        update_status(message=f"唤醒: {result}")
                        result_queue.put({
                            "type": "wake_word", "text": result
                        })
                        reset_idle_timer()
                else:
                    update_status(message=f"识别中: {result[:20]}...")
                    result_queue.put({
                        "type": "mid_text", "text": result
                    })

            elif msg_type == "FIN_TEXT":
                err_no = msg.get("err_no", -1)
                final_result = msg.get("result", "")

                if err_no == 0 and final_result:
                    if is_wake_up_mode:
                        if any(w in final_result for w in WAKE_WORDS):
                            is_wake_up_mode = False
                            update_status(message=f"唤醒: {final_result}")
                            result_queue.put({
                                "type": "wake_word", "text": final_result
                            })
                            reset_idle_timer()
                    else:
                        if any(w in final_result for w in QUIT_WORDS):
                            is_wake_up_mode = True
                            if idle_timer:
                                idle_timer.cancel()
                            update_status(message="等待唤醒词...")
                            result_queue.put({
                                "type": "sleep",
                                "reason": "quit_word",
                                "text": final_result,
                            })
                        else:
                            update_status(message=f"识别: {final_result[:20]}...")
                            result_queue.put({
                                "type": "final_text", "text": final_result
                            })
                            reset_idle_timer()

            elif msg_type == "HEARTBEAT":
                pass

        except json.JSONDecodeError:
            pass

    # ================================================================
    # 主进程命令处理
    # ================================================================
    def check_commands():
        """检查并执行主进程下发的控制命令"""
        nonlocal is_wake_up_mode
        while not command_queue.empty():
            try:
                cmd = command_queue.get_nowait()
                cmd_type = cmd.get("type")

                if cmd_type == "enter_sleep":
                    is_wake_up_mode = True
                    update_status(message="等待唤醒词...")
                    if idle_timer:
                        idle_timer.cancel()

                elif cmd_type == "reset_idle_timer":
                    if not is_wake_up_mode:
                        reset_idle_timer()

                elif cmd_type == "force_wake":
                    is_wake_up_mode = False
                    update_status(message="强制唤醒")
                    result_queue.put({
                        "type": "wake_word", "text": cmd.get("text", "")
                    })
                    reset_idle_timer()

            except Exception:
                break

    # ================================================================
    # 主循环
    # ================================================================
    ws = None
    last_reconnect_time = 0

    try:
        os.environ['ALSA_CARD'] = 'DJI'
        init_audio()

        resampler = AudioResampler(RATE, TARGET_RATE, CHANNELS)
        ready_event.set()
        update_status(is_ready=True, is_running=True, message="麦克风录音就绪")
        print("[Audio-SubProcess] 录音识别子进程已就绪")

        while not stop_event.is_set():
            # 处理主进程命令
            check_commands()

            # WebSocket 连接管理
            if ws is None or not ws.connected:
                now = time.time()
                if now - last_reconnect_time < 0.5:
                    time.sleep(0.05)
                    continue
                try:
                    if ws:
                        try:
                            ws.close()
                        except Exception:
                            pass
                    ws = create_ws()
                    send_start(ws)
                    last_reconnect_time = now
                    update_status(message="百度云已连接")
                except Exception as e:
                    logger.error(f"[Audio-SubProcess] WS 连接失败: {e}")
                    update_status(message=f"WS连接失败: {e}")
                    last_reconnect_time = now
                    time.sleep(0.1)
                    continue

            # 读取音频 -> 重采样 -> 发送百度
            try:
                raw_data = audio_stream.read(
                    CHUNK, exception_on_overflow=False
                )
                resampled = resampler.process(raw_data)
                ws.send_binary(resampled)
            except Exception as e:
                logger.debug(f"[Audio-SubProcess] 发送音频失败: {e}")
                ws = None
                continue

            # 接收百度识别结果
            try:
                ws.settimeout(0.01)
                while True:
                    try:
                        message = ws.recv()
                        if message:
                            on_message(message)
                    except websocket.WebSocketTimeoutException:
                        break
            except Exception:
                ws = None

    except Exception as e:
        set_status_error(str(e))
        error_queue.put(e)
    finally:
        update_status(is_running=False)
        if ws and ws.connected:
            try:
                send_finish(ws)
                ws.close()
            except Exception:
                pass
        close_audio()
        if status_arr:
            try:
                status_arr.close()
            except Exception:
                pass


# ======================================================================
# 主进程端 API
# ======================================================================
class AudioRecordSubProcess:
    """
    麦克风录音 + 语音识别 多进程封装

    - 子进程: 持续录音, 流式发送百度云识别, 检测唤醒词
    - 主进程: 通过 get_result() 获取识别结果事件
    - 支持共享内存状态 (供 mp_show_info 监控)
    - 支持 context manager

    事件类型 (由 get_result 返回):
      {"type": "wake_word",  "text": "..."}                    检测到唤醒词
      {"type": "final_text", "text": "..."}                    最终识别结果
      {"type": "mid_text",   "text": "..."}                    中间识别结果
      {"type": "sleep",      "reason": "idle_timeout|quit_word", "text": "..."}

    用法:
        with AudioRecordSubProcess(config) as audio:
            result = audio.get_result(timeout=5.0)
    """

    def __init__(
        self,
        audio_config: dict = None,
        baidu_config: dict = None,
        recognition_config: dict = None,
        enable_status: bool = False,
    ):
        """
        Args:
            audio_config:  音频参数
                {chunk: 1024, channels: 2, rate: 48000,
                 target_channels: 1, target_rate: 16000}
            baidu_config:  百度云参数
                {appid: "...", appkey: "...", dev_pid: 1537,
                 uri: "ws://vop.baidu.com/realtime_asr"}
            recognition_config: 识别参数
                {vad_silence_time: 1500, idle_timeout: 500.0,
                 wake_words: [...], quit_words: [...]}
            enable_status:  是否启用共享内存状态 (供 mp_show_info 监控)
        """
        self._audio_config = audio_config or {
            'chunk': 1024,
            'channels': 2,
            'rate': 48000,
            'target_channels': 1,
            'target_rate': 16000,
        }
        self._baidu_config = baidu_config or {}
        self._recognition_config = recognition_config or {}
        self._enable_status = enable_status

        # 状态共享内存
        self._status_arr = None
        if enable_status and SharedMemoryArray is not None:
            self._status_arr = SharedMemoryArray.create(
                shape=(8,),
                dtype=np.float64,
            )

        self._result_queue = mp.Queue()
        self._command_queue = mp.Queue()
        self._stop_event = mp.Event()
        self._ready_event = mp.Event()
        self._error_queue = mp.Queue()
        self._process: Optional[mp.Process] = None

    @property
    def status_shm_name(self) -> Optional[str]:
        """获取状态共享内存名称"""
        return self._status_arr.name if self._status_arr else None

    # ---- context manager ----
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    # ---- 生命周期 ----
    def start(self, wait=True, timeout=10.0):
        """启动录音识别子进程"""
        if self._process is not None and self._process.is_alive():
            print("[Audio-SubProcess] 录音进程已在运行")
            return

        self._stop_event.clear()
        self._ready_event.clear()
        while not self._error_queue.empty():
            self._error_queue.get()

        self._process = mp.Process(
            target=_audio_worker,
            args=(
                self._result_queue,
                self._command_queue,
                self._stop_event,
                self._ready_event,
                self._error_queue,
                self._audio_config,
                self._baidu_config,
                self._recognition_config,
                self.status_shm_name,
            ),
            daemon=True,
        )
        self._process.start()

        if wait:
            if not self._ready_event.wait(timeout=timeout):
                if not self._error_queue.empty():
                    err = self._error_queue.get()
                    raise RuntimeError(
                        f"[Audio-SubProcess] 子进程初始化失败: {err}"
                    ) from err
                raise TimeoutError(
                    f"[Audio-SubProcess] 子进程未在 {timeout}s 内就绪"
                )

        ac = self._audio_config
        print(
            f"[Audio-SubProcess] 已启动 "
            f"({ac['rate']}Hz {ac['channels']}ch -> "
            f"{ac['target_rate']}Hz {ac['target_channels']}ch)"
        )

    def stop(self, wait=True):
        """停止录音识别子进程"""
        self._stop_event.set()

        if self._process is not None:
            if wait:
                self._process.join(timeout=5.0)
                if self._process.is_alive():
                    self._process.kill()
                    self._process.join(timeout=2.0)
            self._process = None

        # 释放状态共享内存
        if self._status_arr:
            try:
                self._status_arr.close()
                self._status_arr.unlink()
            except Exception:
                pass
            self._status_arr = None

        print("[Audio-SubProcess] 已停止")

    @property
    def is_ready(self) -> bool:
        """子进程是否就绪"""
        return self._ready_event.is_set()

    # ---- 数据读取 ----
    def get_result(self, timeout: float = None):
        """
        获取识别结果事件 (阻塞)

        Args:
            timeout: 超时秒数, None 表示一直等待

        Returns:
            dict: 识别结果事件, 例如
                {"type": "wake_word", "text": "考拉一号"}
                {"type": "final_text", "text": "帮我拿可乐"}
                {"type": "sleep", "reason": "idle_timeout"}
            None: 超时无结果
        """
        try:
            return self._result_queue.get(timeout=timeout)
        except Exception:
            return None

    def get_result_nowait(self):
        """非阻塞获取识别结果 (无结果返回 None)"""
        try:
            return self._result_queue.get_nowait()
        except Exception:
            return None

    # ---- 控制命令 ----
    def enter_sleep(self):
        """命令子进程进入休眠模式 (停止响应指令, 等待唤醒词)"""
        self._command_queue.put({"type": "enter_sleep"})

    def reset_idle_timer(self):
        """重置子进程的空闲计时器 (主进程完成指令处理后调用)"""
        self._command_queue.put({"type": "reset_idle_timer"})

    def force_wake(self, text: str = ""):
        """强制唤醒子进程 (用于手动/测试模式)"""
        self._command_queue.put({"type": "force_wake", "text": text})


# ======================================================================
# 便捷测试
# ======================================================================
if __name__ == "__main__":
    print("--- AudioRecord 多进程测试 ---")

    audio = AudioRecordSubProcess(
        baidu_config={
            'appid': 'YOUR_APPID',
            'appkey': 'YOUR_APPKEY',
            'dev_pid': 1537,
            'uri': 'ws://vop.baidu.com/realtime_asr',
        },
        recognition_config={
            'wake_words': ['考拉一号', '考拉1号'],
            'quit_words': ['退下', '休息'],
            'idle_timeout': 120.0,
        },
        enable_status=True,
    )

    audio.start()

    try:
        for i in range(100):
            result = audio.get_result(timeout=5.0)
            if result:
                t = result.get('type')
                text = result.get('text', '')
                reason = result.get('reason', '')
                print(f"[{i+1}] type={t}, text={text}, reason={reason}")
            else:
                print(f"[{i+1}] 等待中...")
    except KeyboardInterrupt:
        print("\n退出测试")
    finally:
        audio.stop()
