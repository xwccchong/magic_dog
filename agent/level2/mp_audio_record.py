#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦克风录音多进程模块 (兼容入口)

录音与识别已合并到 mp_audio_recognization.py 中统一管理,
本文件仅做重导出以保持向后兼容。
"""
from .mp_audio_recognization import AudioRecordSubProcess

__all__ = ["AudioRecordSubProcess"]
