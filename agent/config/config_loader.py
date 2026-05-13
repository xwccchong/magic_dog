# -*- coding: utf-8 -*-
"""
配置加载器
支持动态加载不同的 LLM prompt 文件
"""
import os
import json

# 配置文件目录
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

# 基础配置文件路径 (固定)
CONFIG_FILE = os.path.join(CONFIG_DIR, "server_config.json")
# 默认的 Prompt 文件名
DEFAULT_PROMPT_NAME = "llm_prompt_v1.txt"

class Config:
    """配置类，存储所有配置参数"""

    _instance = None
    _config = None
    _llm_prompt = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, prompt_filename=None):
        """
        加载配置文件
        :param prompt_filename: 指定要加载的 prompt 文件名 (例如 "prompt_custom.txt")
        """
        # 1. 加载固定的 JSON 配置
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

        # 2. 确定要加载的 Prompt 文件路径
        target_prompt_name = prompt_filename if prompt_filename else DEFAULT_PROMPT_NAME
        prompt_path = os.path.join(CONFIG_DIR, target_prompt_name)

        # 3. 加载指定的 LLM prompt
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self._llm_prompt = f.read()
        else:
            raise FileNotFoundError(f"未找到指定的 Prompt 文件: {prompt_path}")

        return self

    @property
    def llm_prompt(self):
        """获取当前加载的 LLM Prompt"""
        return self._llm_prompt

    # ... 其他 property 保持不变 ...
    @property
    def websocket(self): return self._config.get("websocket", {})
    @property
    def microphone(self): return self._config.get("microphone", {})
    @property
    def voice_recognition(self): return self._config.get("voice_recognition", {})
    @property
    def llm(self): return self._config.get("llm", {})
    @property
    def timing(self): return self._config.get("timing", {})
    @property
    def wake_words(self): return self._config.get("wake_words", [])
    @property
    def quit_words(self): return self._config.get("quit_words", [])
    @property
    def exhibition_phrases(self): return self._config.get("exhibition_phrases", [])
    @property
    def greetings(self): return self._config.get("greetings", {})
    @property
    def paths(self): return self._config.get("paths", {})

    def get(self, key, default=None):
        """获取配置项"""
        return self._config.get(key, default)

# 全局配置实例
config = Config()

def load_config(prompt_filename=None):
    """
    加载配置并返回配置对象
    :param prompt_filename: 可选，传入特定的 prompt 文件名
    """
    return config.load(prompt_filename)

def get_config():
    """获取配置实例（默认加载）"""
    if config._config is None:
        config.load()
    return config