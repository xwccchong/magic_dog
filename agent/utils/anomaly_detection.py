#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测模块 (Anomaly Detection)

独立封装，可被 client 作为原子技能直接调用。
从 agent/config/ 读取 LLM 配置和 AD prompt。

用法:
    from agent.utils.anomaly_detection import detect_anomaly

    result = detect_anomaly(image_base64)
    if result and result["is_anomaly"]:
        # 处理异常
"""

import os
import sys
import json
import logging
import time

# 将 agent/ 加入 sys.path，确保能 import agent.config
_AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _AGENT_DIR not in sys.path:
    sys.path.insert(0, _AGENT_DIR)

from config.config_loader import load_config
from openai import OpenAI

logger = logging.getLogger(__name__)

# ---- 模块级初始化: 加载配置 ----
# 多视角拍摄时使用AD_pro_prompt，单视角时使用AD_prompt
config = load_config(prompt_filename="AD_pro_prompt.txt")

_llm_config = config.llm
_llm_prompt = config.llm_prompt

_client = OpenAI(
    api_key=_llm_config.get("api_key"),
    base_url=_llm_config.get("base_url"),
)

_DEFAULT_QUESTION = "请分析这张图片中的桌面状态，是否存在异常？"

# ---- 巡检总结 Prompt ----
_SUMMARY_PROMPT = """你是一个巡检总结播报员。根据以下巡检点的检测结果，生成一段简洁、口语化的巡检总结，适合语音播报。

要求：
1. 提供一个整体评价，包括总共巡检了几个点，逐个点简要说明状态（正常/异常），如果有异常，说清楚哪个点发现了什么。
2. 语气自然友好，不要用 JSON 格式，直接输出纯文本，不要输出表情符号"""

def detect_anomaly(image_base64: str, text: str = None):
    """
    使用视觉大模型分析图像进行异常检测

    Args:
        image_base64: base64 编码的 JPEG 图像数据
        text:         附加文本提示 (默认使用内置提示)

    Returns:
        dict: {"is_anomaly": bool, "confidence": float,
               "description": str, "objects": list}
        None: 如果检测失败
    """
    question = text or _DEFAULT_QUESTION
    print(f"\n🔍 [AnomalyDetection] 视觉异常检测分析中...")
    start_time = time.time()

    try:
        response = _client.chat.completions.create(
            model=_llm_config.get("vision_model", "qwen-omni-turbo"),
            messages=[
                {
                    "role": "system",
                    "content": _llm_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                        {
                            "type": "text",
                            "text": question,
                        },
                    ],
                },
            ],
            temperature=0,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        llm_cost = time.time() - start_time
        content = response.choices[0].message.content.strip()
        print(f"   📥 异常检测结果:\n{content}")
        print(f"⏱️ [耗时分析] 视觉异常检测耗时: {llm_cost:.2f} 秒")

        return json.loads(content)

    except Exception as e:
        print(f"❌ [AnomalyDetection] 异常检测失败: {e}")
        logger.error(f"异常检测失败: {e}")
        return None


def summarize_inspection(results: list) -> str:
    """
    将多个巡检点的结果发给 LLM 生成总结

    Args:
        results: 检测结果列表, 每项包含 {"location", "is_anomaly", "description", "objects", ...}

    Returns:
        str: 总结文本
        None: 如果生成失败
    """
    if not results:
        return None

    print(f"\n📊 [AnomalyDetection] 生成巡检总结 ({len(results)} 个点位)...")
    start_time = time.time()

    # 拼接巡检结果
    lines = []
    for i, r in enumerate(results, 1):
        loc = r.get("location", f"点位{i}")
        is_anomaly = r.get("is_anomaly", False)
        desc = r.get("description", "")
        objects = r.get("objects", [])
        if is_anomaly:
            obj_str = "、".join(objects) if objects else "未知物品"
            lines.append(f"第{i}个点({loc}): 异常 - {desc}，发现: {obj_str}")
        else:
            lines.append(f"第{i}个点({loc}): 正常 - {desc}")

    result_text = "\n".join(lines)

    try:
        response = _client.chat.completions.create(
            model=_llm_config.get("model", "qwen-turbo"),
            messages=[
                {"role": "system", "content": _SUMMARY_PROMPT},
                {"role": "user", "content": f"以下是巡检结果:\n{result_text}\n\n请生成巡检总结。"},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        llm_cost = time.time() - start_time
        summary = response.choices[0].message.content.strip()
        print(f"   📥 巡检总结:\n{summary}")
        print(f"⏱️ [耗时分析] 总结生成耗时: {llm_cost:.2f} 秒")
        return summary

    except Exception as e:
        print(f"❌ [AnomalyDetection] 巡检总结生成失败: {e}")
        logger.error(f"巡检总结生成失败: {e}")
        return None