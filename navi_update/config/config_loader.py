# -*- coding: utf-8 -*-
"""
配置加载器
从 config 目录加载 JSON 配置文件和文本文件
"""
import os
import json

# 配置文件目录
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径
CONFIG_FILE = os.path.join(CONFIG_DIR, "server_config.json")
LLM_PROMPT_FILE = os.path.join(CONFIG_DIR, "llm_prompt_v1.txt")


class Config:
    """配置类，存储所有配置参数"""

    _instance = None
    _config = None
    _llm_prompt = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        """加载配置文件"""
        # 加载 JSON 配置
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

        # 加载 LLM prompt
        with open(LLM_PROMPT_FILE, 'r', encoding='utf-8') as f:
            self._llm_prompt = f.read()

        return self

    @property
    def websocket(self):
        """WebSocket 配置"""
        return self._config.get("websocket", {})

    @property
    def microphone(self):
        """麦克风配置"""
        return self._config.get("microphone", {})

    @property
    def voice_recognition(self):
        """语音识别配置"""
        return self._config.get("voice_recognition", {})

    @property
    def llm(self):
        """LLM 配置"""
        return self._config.get("llm", {})

    @property
    def llm_prompt(self):
        """LLM Prompt"""
        return self._llm_prompt

    @property
    def timing(self):
        """时间相关配置"""
        return self._config.get("timing", {})

    @property
    def wake_words(self):
        """唤醒词列表"""
        return self._config.get("wake_words", [])

    @property
    def quit_words(self):
        """退出词列表"""
        return self._config.get("quit_words", [])

    @property
    def exhibition_phrases(self):
        """展览模式短语列表"""
        return self._config.get("exhibition_phrases", [])

    @property
    def greetings(self):
        """问候语"""
        return self._config.get("greetings", {})

    @property
    def paths(self):
        """路径配置"""
        return self._config.get("paths", {})

    def get(self, key, default=None):
        """获取配置项"""
        return self._config.get(key, default)


# 全局配置实例
config = Config()


def load_config():
    """加载配置并返回配置对象"""
    return config.load()


def get_config():
    """获取配置实例"""
    if config._config is None:
        config.load()
    return config
