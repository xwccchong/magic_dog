#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS 语音播报多进程模块

架构 (参考 mp_audio_recognization):
- 子进程: 独立 mp.Process, 持续运行, 通过阿里云 TTS 合成并通过 Go2 扬声器播放
- 主进程: 通过 mp.Queue 发送文本, 子进程即时播报
- 共享内存: 写入状态供 mp_show_info 监控

主进程向队列中添加播报的信息；子进程以10hz频率读取队列中状态，进行播报

优势:
  - 长连接复用, 消除每次播放的连接延迟
  - TTS 播报完全在子进程, 不阻塞主进程
  - 主进程只需 put(text) 即可触发播报
  - 共享内存状态可被外部监控读取

用法:
    tts = TTSPlayerSubProcess(enable_status=True)
    tts.start()

    # 发送文本播报 (非阻塞)
    tts.speak("帮我拿可乐")

    # 或者阻塞等待播报完成
    tts.speak_and_wait("你好呀")

    tts.stop()
"""

import os
import sys
import time
import wave
import base64
import logging
import tempfile
import multiprocessing as mp
import threading

logger = logging.getLogger(__name__)

# 导入共享内存模块
try:
    from shared_memory_buffer import SharedMemoryArray
except ImportError:
    SharedMemoryArray = None


# ======================================================================
# 子进程入口: TTS 合成 + Go2 扬声器播放
# ======================================================================
def _tts_worker(
    text_queue: mp.Queue,
    result_queue: mp.Queue,
    stop_event: mp.Event,
    ready_event: mp.Event,
    error_queue: mp.Queue,
    dashscope_api_key: str,
    voice: str = "Cherry",
    instructions: str = "语气可爱霸道一点，简短回复。",
    status_shm_name: str = None,
):
    """
    子进程入口: 持续监听文本队列, 进行 TTS 播报

    Args:
        text_queue:    主进程 -> 子进程 (待播报文本)
        result_queue:  主进程 <- 子进程 (播报完成事件)
        stop_event:    停止信号
        ready_event:   就绪信号
        error_queue:   错误上报
        dashscope_api_key: 阿里云 API Key
        voice:         TTS 音色
        instructions:  TTS 指令
        status_shm_name: 状态共享内存名称 (用于 mp_show_info 监控)
    """
    import dashscope
    from dashscope.audio.qwen_tts_realtime import *

    # ---- 子进程内导入 Go2 SDK ----
    sys.path.insert(0, '/home/unitree/dky/go2_python_sdk2')
    from unitree_sdk2py.core.dds.channel import DDSChannelFactoryInitialize
    from unitree_sdk2py.sdk.sdk import create_standard_sdk
    from unitree_sdk2py.go2.audiohub.audiohub_client import AudioHubClient

    # ---- 初始化 ----
    dashscope.api_key = dashscope_api_key

    go2_audio_client = None
    ws_tts = None

    # ---- 共享内存状态 ----
    # 布局: [is_ready, is_running, error_flag, is_speaking, padding..., last_update]
    status_arr = None
    if status_shm_name and SharedMemoryArray is not None:
        try:
            status_arr = SharedMemoryArray.connect(
                name=status_shm_name,
                shape=(8,),
                dtype=np.float64,
            )
            logger.info(f"[TTS-SubProcess] 已连接状态共享内存: {status_shm_name}")
        except Exception as e:
            logger.warning(f"[TTS-SubProcess] 无法连接状态共享内存: {e}")

    def update_status(is_ready=None, is_running=None, error_flag=None,
                      is_speaking=None, message=None):
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
            if is_speaking is not None:
                data[3] = 1.0 if is_speaking else 0.0
            data[7] = time.time()  # last_update
            status_arr.write(data)
        except Exception:
            pass

    def set_status_error(error_msg: str):
        """设置错误状态"""
        update_status(error_flag=True)

    def clear_status_error():
        """清除错误状态"""
        update_status(error_flag=False)

    # ================================================================
    # 回调类
    # ================================================================
    class TTSCallback(QwenTtsRealtimeCallback):
        def __init__(self):
            self.complete_event = threading.Event()
            self.audio_bytes = bytearray()

        def on_open(self):
            pass

        def on_close(self, code, msg):
            pass

        def on_event(self, response):
            try:
                event_type = response["type"]
                if event_type == "response.audio.delta":
                    audio = base64.b64decode(response["delta"])
                    self.audio_bytes.extend(audio)
                elif event_type == "session.finished":
                    self.complete_event.set()
            except Exception:
                pass

        def wait_for_finished(self):
            self.complete_event.wait()

    # ================================================================
    # Go2 音频客户端初始化
    # ================================================================
    def init_go2_audio():
        """初始化 Go2 音频客户端
        调用底层DDS通信，建立机器狗扬声器"""
        nonlocal go2_audio_client
        try:
            sdk = create_standard_sdk('UnitreeGo2SDK')
            communicator = DDSChannelFactoryInitialize(domainId=0, networkInterface="eth0")
            robot = sdk.create_robot(communicator, serialNumber='B42D2000XXXXXXXX')

            go2_audio_client = robot.ensure_client(AudioHubClient.default_service_name)
            go2_audio_client.SetTimeout(3.0)
            go2_audio_client.Init()
            logger.info("[TTS-SubProcess] Go2 音频客户端初始化成功")
            update_status(message="Go2 音频就绪")
        except Exception as e:
            logger.error(f"[TTS-SubProcess] Go2 音频客户端初始化失败: {e}")
            set_status_error(f"Go2初始化失败: {e}")
            raise

    # ================================================================
    # TTS WebSocket 管理
    # ================================================================
    def create_tts_connection():
        """创建 TTS WebSocket 连接
        连接TTS API"""
        nonlocal ws_tts
        if ws_tts and hasattr(ws_tts, 'connected') and ws_tts.connected:
            return ws_tts

        callback = TTSCallback()
        ws_tts = QwenTtsRealtime(
            model="qwen-tts-realtime",
            callback=callback,
            url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
        )
        ws_tts.connect()
        ws_tts.update_session(
            voice=voice,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode="streaming",
            instructions=instructions
        )
        update_status(message="TTS 连接就绪")
        return ws_tts, callback

    def close_tts_connection():
        """关闭 TTS 连接"""
        nonlocal ws_tts
        if ws_tts:
            try:
                ws_tts.close()
            except Exception:
                pass
            ws_tts = None

    # ================================================================
    # 核心播报函数
    # ================================================================
    def do_speak(text: str):
        """
        执行一次 TTS 播报

        Args:
            text: 要播报的文本

        Returns:
            bool: 是否成功播报
            float: 播报时长
        """
        nonlocal go2_audio_client, ws_tts

        try:
            tts_start = time.time()
            update_status(is_speaking=True, message=f"合成中: {text[:15]}...")

            # 确保 TTS 连接可用
            if ws_tts is None or not hasattr(ws_tts, 'connected') or not ws_tts.connected:
                ws_tts, callback = create_tts_connection()
            else:
                callback = TTSCallback()

            # 发送文本并等待合成
            ws_tts.append_text(text)
            ws_tts.finish()
            callback.wait_for_finished()

            wait_cost = time.time() - tts_start

            # 合成音频
            if len(callback.audio_bytes) == 0:
                update_status(message="合成失败")
                return False, 0.0

            # 写临时 WAV 文件
            handle, tmp_wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(handle)

            with wave.open(tmp_wav_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(callback.audio_bytes)

            # 计算音频时长
            duration = len(callback.audio_bytes) / (24000.0 * 2.0)

            # 发送到 Go2 扬声器
            if go2_audio_client:
                update_status(message=f"播放中 ({duration:.1f}s)")
                go2_audio_client.MegaphoneEnter()
                go2_audio_client.MegaphoneUpload(tmp_wav_path)

                # 等待播完
                time.sleep(duration + 0.2)
                go2_audio_client.MegaphoneExit()

            # 清理临时文件
            try:
                os.remove(tmp_wav_path)
            except Exception:
                pass

            update_status(is_speaking=False, message="TTS 就绪")
            logger.info(
                f"[TTS-SubProcess] 播报完成: '{text[:20]}...' "
                f"(TTS: {wait_cost:.2f}s, 时长: {duration:.2f}s)"
            )
            return True, duration

        except Exception as e:
            logger.error(f"[TTS-SubProcess] 播报失败: {e}")
            update_status(is_speaking=False, error_flag=True, message=f"播报失败: {e}")
            return False, 0.0

    # ================================================================
    # 主循环
    # ================================================================
    try:
        # 初始化 Go2 音频客户端
        init_go2_audio()

        # 预热 TTS 连接
        create_tts_connection()

        ready_event.set()
        update_status(is_ready=True, is_running=True, message="TTS 就绪")
        print("[TTS-SubProcess] TTS 播报子进程已就绪 (长连接已预热)")

        while not stop_event.is_set():
            # 进入死循环，当stop_event设置之后才会退出
            # 非阻塞检查文本队列
            try:
                # 10帧的频率拿文本信息
                item = text_queue.get(timeout=0.1)
            except:
                continue

            # 解析消息
            if isinstance(item, str):
                text = item
                block = False
            elif isinstance(item, dict):
                text = item.get('text', '')
                block = item.get('block', False)
            else:
                continue

            if not text:
                continue

            # 执行播报
            success, duration = do_speak(text)

            # 如果要求阻塞等待, 这里已经等待完毕
            result_queue.put({
                'type': 'done',
                'text': text,
                'success': success,
                'duration': duration,
            })

    except Exception as e:
        set_status_error(str(e))
        error_queue.put(e)
    finally:
        update_status(is_running=False, is_speaking=False)
        close_tts_connection()
        if status_arr:
            try:
                status_arr.close()
            except Exception:
                pass
        print("[TTS-SubProcess] TTS 播报子进程已停止")


# ======================================================================
# 主进程端 API
# ======================================================================
class TTSPlayerSubProcess:
    """
    TTS 语音播报多进程封装

    - 子进程: 持续运行, 接收文本队列, 进行 TTS 播报
    - 主进程: 通过 speak() 发送文本, 即时触发播报
    - 支持长连接复用, 消除每次播放的连接延迟
    - 支持共享内存状态 (供 mp_show_info 监控)
    - 支持 context manager

    用法:
        with TTSPlayerSubProcess() as tts:
            tts.speak("帮我拿可乐")           # 非阻塞
            tts.speak_and_wait("你好呀")       # 阻塞等待播完
    """

    def __init__(
        self,
        dashscope_api_key: str = None,
        voice: str = "Cherry",
        instructions: str = "语气可爱霸道一点，简短回复。",
        enable_status: bool = False,
    ):
        """
        Args:
            dashscope_api_key: 阿里云 API Key, 默认从环境变量获取
            voice: TTS 音色 (如 "Cherry", "Aria" 等)
            instructions: TTS 指令/风格
            enable_status:  是否启用共享内存状态 (供 mp_show_info 监控)
        """
        # 获取 API Key
        if dashscope_api_key is None:
            import dashscope
            if 'DASHSCOPE_API_KEY' in os.environ:
                dashscope_api_key = os.environ['DASHSCOPE_API_KEY']
            else:
                dashscope_api_key = 'sk-10c321e6f4ee425095605a75cb4aa3ec'

        self._api_key = dashscope_api_key
        self._voice = voice
        self._instructions = instructions
        self._enable_status = enable_status

        # 状态共享内存
        self._status_arr = None
        if enable_status and SharedMemoryArray is not None:
            self._status_arr = SharedMemoryArray.create(
                shape=(8,),
                dtype=np.float64,
            )

        self._text_queue = mp.Queue()
        self._result_queue = mp.Queue()
        self._stop_event = mp.Event()
        self._ready_event = mp.Event()
        self._error_queue = mp.Queue()
        self._process: mp.Process = None

    @property
    def status_shm_name(self) -> str:
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
        """启动 TTS 播报子进程"""
        if self._process is not None and self._process.is_alive():
            print("[TTS] TTS 进程已在运行")
            return self

        self._stop_event.clear()
        self._ready_event.clear()
        while not self._error_queue.empty():
            self._error_queue.get()

        self._process = mp.Process(
            target=_tts_worker,
            args=(
                self._text_queue,
                self._result_queue,
                self._stop_event,
                self._ready_event,
                self._error_queue,
                self._api_key,
                self._voice,
                self._instructions,
                self.status_shm_name,
            ),
            daemon=True,
        )
        self._process.start()

        # 阻塞模式，等待子进程启动好之后才能退出wait
        if wait:
            if not self._ready_event.wait(timeout=timeout):
                if not self._error_queue.empty():
                    err = self._error_queue.get()
                    raise RuntimeError(f"[TTS] 子进程初始化失败: {err}") from err
                raise TimeoutError(f"[TTS] 子进程未在 {timeout}s 内就绪")

        print(f"[TTS] TTS 播报子进程已启动 (音色: {self._voice})")
        return self

    def stop(self, wait=True):
        """停止 TTS 播报子进程"""
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

        print("[TTS] TTS 播报子进程已停止")

    @property
    def is_ready(self) -> bool:
        """子进程是否就绪"""
        return self._ready_event.is_set()

    # ---- 核心 API ----
    def speak(self, text: str, block: bool = False):
        """
        发送文本进行播报 (非阻塞)

        Args:
            text: 要播报的文本
            block: 是否阻塞等待播报完成

        Returns:
            bool: 是否成功放入队列
        """
        try:
            self._text_queue.put({'text': text, 'block': block}, timeout=1.0)
            return True
        except Exception as e:
            logger.error(f"[TTS] 放入队列失败: {e}")
            return False

    def speak_and_wait(self, text: str, timeout: float = 30.0):
        """
        发送文本并阻塞等待播报完成

        Args:
            text: 要播报的文本
            timeout: 最大等待时间

        Returns:
            bool: 是否成功播报
        """
        self.speak(text, block=True)

        try:
            result = self._result_queue.get(timeout=timeout)
            return result.get('success', False)
        except Exception:
            return False

    def get_result(self, timeout: float = None):
        """
        获取播报完成事件 (用于异步模式)

        Returns:
            dict: {'type': 'done', 'text': ..., 'success': ..., 'duration': ...}
            None: 超时无结果
        """
        try:
            return self._result_queue.get(timeout=timeout)
        except Exception:
            return None


# ======================================================================
# 便捷测试
# ======================================================================
if __name__ == "__main__":
    print("--- TTS 多进程播报测试 ---\n")

    tts = TTSPlayerSubProcess(
        voice="Cherry",
        instructions="语气可爱霸道一点，简短回复。",
        enable_status=True,
    )

    tts.start()

    try:
        # 测试非阻塞播报
        print("测试1: 非阻塞播报")
        tts.speak("你好呀，我是考拉一号")

        # 等待播报完成
        result = tts.get_result(timeout=30.0)
        if result:
            print(f"播报完成: success={result.get('success')}, duration={result.get('duration'):.2f}s")

        # 测试阻塞播报
        print("\n测试2: 阻塞播报")
        tts.speak_and_wait("现在我要说一个很长的句子来测试阻塞功能")

        # 连续快速播报 (测试队列)
        print("\n测试3: 快速连续播报")
        tts.speak("第一句")
        tts.speak("第二句")
        tts.speak("第三句")

        # 等待所有完成
        for i in range(3):
            result = tts.get_result(timeout=30.0)
            if result:
                print(f"  -> 第{i+1}句完成")

        print("\n所有测试完成!")

    except KeyboardInterrupt:
        print("\n退出测试")
    finally:
        tts.stop()
