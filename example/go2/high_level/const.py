# -*- coding: utf-8 -*-
"""
常量
"""
import uuid

# 下面2个是鉴权信息
APPID = 121922282

APPKEY = "kC8gE8nr8kqd8nvzKmVuwYbc"

# 语言模型 ， 可以修改为其它语言模型测试，如远场普通话19362
DEV_PID = 1537

# 生成唯一的会话ID
SESSION_ID = str(uuid.uuid4())

# 可以改为wss://，添加 sn 参数
URI = f"wss://vop.baidu.com/realtime_asr?sn={SESSION_ID}"