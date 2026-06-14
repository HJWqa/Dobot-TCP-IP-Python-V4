#!/usr/bin/env python3
"""
本地测试脚本 — 连接 mock_dobot_server.py 测试完整流程。
"""
import sys
import time
from DobotDemo import DobotDemo

# 用 localhost 替代真实机器人 IP
dobot = DobotDemo("127.0.0.1")

try:
    dobot.start()
except KeyboardInterrupt:
    print("\n测试结束")
