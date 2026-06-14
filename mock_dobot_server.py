#!/usr/bin/env python3
"""
Mock Dobot server — 模拟机械臂的 Dashboard(29999) 和 Feedback(30004) 端口。
用于本地测试，不需要真实机械臂。
"""
import socket
import struct
import threading
import time


def start_dashboard_server(host="127.0.0.1", port=29999):
    """模拟 Dashboard 端口 (29999)，响应指令调用"""

    def handle(conn, addr):
        print(f"[Dashboard] 连接来自 {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode("utf-8").strip()
                print(f"[Dashboard] 收到: {msg}")

                # 模拟不同指令的返回值
                if msg.startswith("EnableRobot"):
                    reply = "0,{a2e8f1b3-4c5d-4a6e-8b9d-1f2e3d4c5b6a}"
                elif msg.startswith("DisableRobot"):
                    reply = "0,{}"
                elif msg.startswith("MovJ"):
                    reply = "0,{b3f9e2c4-5d6e-4b7f-9c0d-2e3f4d5c6b7a}"
                elif msg.startswith("MovL"):
                    reply = "0,{c4f0e3d5-6e7f-4c8a-0d1e-3f4e5d6c7b8a}"
                elif msg == "RobotMode()":
                    reply = "0,5"
                elif msg == "ClearError()":
                    reply = "0,{}"
                elif msg == "ResetRobot()":
                    reply = "0,{}"
                elif msg == "SpeedFactor(100)":
                    reply = "0,{}"
                else:
                    # 默认返回成功
                    reply = f"0,{{test-{msg[:20]}}}"

                print(f"[Dashboard] 回复: {reply}")
                conn.sendall(reply.encode("utf-8"))

        except (ConnectionResetError, BrokenPipeError):
            print("[Dashboard] 客户端断开")
        finally:
            conn.close()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    print(f"[Dashboard] 监听 {host}:{port}")
    while True:
        conn, addr = sock.accept()
        t = threading.Thread(target=handle, args=(conn, addr), daemon=True)
        t.start()


def start_feedback_server(host="127.0.0.1", port=30004):
    """模拟 Feedback 端口 (30004)，周期性发送机器人状态数据包"""

    # 构建与 dobot_api.py MyType 匹配的 numpy dtype 对应的 struct 格式
    # 实际反馈数据用 raw bytes 发送，这里简化模拟主要字段
    def build_feedback_packet():
        """构建一个最小化的合法反馈数据包"""
        buf = bytearray()
        # len (uint16) — 数据包总长度标识
        total_len = 1440
        buf += struct.pack("<H", total_len)  # uint16
        # reserve (6 bytes)
        buf += b"\x00" * 6
        # DigitalInputs (uint64)
        buf += struct.pack("<Q", 0b00000001)
        # DigitalOutputs (uint64)
        buf += struct.pack("<Q", 0b00000010)
        # RobotMode (uint64)
        buf += struct.pack("<Q", 5)
        # TimeStamp (uint64)
        buf += struct.pack("<Q", int(time.time() * 1000))
        # RunTime (uint64)
        buf += struct.pack("<Q", 12345)
        # TestValue (uint64) — 必须是 0x123456789abcdef 才会被解析
        buf += struct.pack("<Q", 0x123456789ABCDEF)
        # reserve2 (8 bytes)
        buf += b"\x00" * 8
        # SpeedScaling (float64)
        buf += struct.pack("<d", 100.0)
        # reserve3 (16 bytes)
        buf += b"\x00" * 16
        # VRobot (float64)
        buf += struct.pack("<d", 0.0)
        # IRobot (float64)
        buf += struct.pack("<d", 0.0)
        # ProgramState (float64)
        buf += struct.pack("<d", 1.0)
        # SafetyOIn (uint16)
        buf += struct.pack("<H", 0)
        # SafetyOOut (uint16)
        buf += struct.pack("<H", 0)
        # reserve4 (76 bytes)
        buf += b"\x00" * 76
        # QTarget (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 10.0)
        # QDTarget (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # QDDTarget (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # ITarget (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # MTarget (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # QActual (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 20.0)
        # QDActual (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # IActual (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # ActualTCPForce (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # ToolVectorActual (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # TCPSpeedActual (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # TCPForce (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # ToolVectorTarget (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # TCPSpeedTarget (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # MotorTemperatures (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 30.0)
        # JointModes (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 1.0)
        # VActual (6 x float64)
        for _ in range(6):
            buf += struct.pack("<d", 0.0)
        # HandType (4 bytes)
        buf += b"\x00" * 4
        # 剩下的简单字段 padding 到 1440 字节
        remaining = total_len - len(buf)
        if remaining > 0:
            buf += b"\x00" * remaining

        return bytes(buf[:total_len])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    print(f"[Feedback] 监听 {host}:{port}")

    while True:
        conn, addr = sock.accept()
        print(f"[Feedback] 连接来自 {addr}")
        try:
            while True:
                packet = build_feedback_packet()
                try:
                    conn.sendall(packet)
                except (ConnectionResetError, BrokenPipeError):
                    break
                time.sleep(0.5)  # 每 500ms 发一次状态
        except Exception as e:
            print(f"[Feedback] 异常: {e}")
        finally:
            conn.close()
            print("[Feedback] 客户端断开")


if __name__ == "__main__":
    print("🚀 启动 Mock Dobot 服务器...")
    print("   Dashboard : 127.0.0.1:29999")
    print("   Feedback  : 127.0.0.1:30004")
    print()

    dash = threading.Thread(target=start_dashboard_server, daemon=True)
    feed = threading.Thread(target=start_feedback_server, daemon=True)

    dash.start()
    feed.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 关闭 Mock 服务器")
