# -*- coding: utf-8 -*-

import re

# Config
HOST = '0.0.0.0'  # 监听地址
PORT = 5000  # 监听端口

# 定义白名单列表
WHITE_LIST_DOMAINS = [
    re.compile(r'^(?:https?://)?httpbin\.org(:\d+)?.*$'),
    re.compile(r'^(?:https?://)?1\.1\.1\.1(:\d+)?.*$'),
]
