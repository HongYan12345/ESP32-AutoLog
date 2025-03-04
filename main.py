import network
import time
import json
import socket
import config
from machine import Timer

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('连接到WiFi...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('WiFi已连接')
    print('IP地址:', wlan.ifconfig()[0])

class WebSocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.timer = None
        self.connected = False
        
    def connect(self):
        try:
            self.socket = socket.socket()
            addr = socket.getaddrinfo(self.host, self.port)[0][-1]
            self.socket.connect(addr)
            
            # WebSocket 握手
            key = "dGhlIHNhbXBsZSBub25jZQ=="
            handshake = (
                f"GET / HTTP/1.1\r\n"
                f"Host: {self.host}:{self.port}\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\n"
                "Sec-WebSocket-Version: 13\r\n"
                "\r\n"
            )
            self.socket.send(handshake.encode())
            
            response = self.socket.recv(1024).decode()
            if "101 Switching Protocols" in response:
                print(f"连接websocket服务器成功 at ws://{self.host}:{self.port}")
                self.connected = True
                self.start_heartbeat()
                return True
        except Exception as e:
            print(f"连接失败: {str(e)}")
            self.close()
            return False
            
    def send(self, message, is_binary=False):
        if not self.connected:
            return False
            
        try:
            opcode = 0x2 if is_binary else 0x1
            payload = message.encode() if isinstance(message, str) else message
            length = len(payload)
            
            # 构建 WebSocket 帧
            frame = bytearray([0x80 | opcode])
            
            if length < 126:
                frame.append(length)
            elif length < 65536:
                frame.append(126)
                frame.extend(length.to_bytes(2, 'big'))
            else:
                frame.append(127)
                frame.extend(length.to_bytes(8, 'big'))
                
            frame.extend(payload)
            self.socket.send(frame)
            return True
        except Exception as e:
            print(f"发送失败: {str(e)}")
            self.close()
            return False
            
    def receive(self):
        if not self.connected:
            return None
            
        try:
            # 读取帧头
            header = self.socket.recv(2)
            if not header:
                return None
                
            opcode = header[0] & 0x0F
            length = header[1] & 0x7F
            
            if length == 126:
                length = int.from_bytes(self.socket.recv(2), 'big')
            elif length == 127:
                length = int.from_bytes(self.socket.recv(8), 'big')
                
            data = self.socket.recv(length)
            if opcode == 0x1:
                return data.decode()
            return data
        except Exception as e:
            print(f"接收失败: {str(e)}")
            self.close()
            return None
            
    def heartbeat(self, timer):
        if self.connected:
            print("发送心跳消息至服务器")
            self.send("ping")
            
    def start_heartbeat(self):
        self.timer = Timer(-1)
        self.timer.init(period=config.WEBSOCKET_RETRY_INTERVAL * 1000, mode=Timer.PERIODIC, callback=self.heartbeat)
        
    def close(self):
        self.connected = False
        if self.timer:
            self.timer.deinit()
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

def main():
    connect_wifi()
    ws = WebSocketClient(config.SERVER_HOST, config.SERVER_PORT)
    
    while True:
        if ws.connect():
            # 发送测试消息
            ws.send("你好, 我是ESP")
            print("发送测试消息")
            
            # 持续接收消息
            while ws.connected:
                message = ws.receive()
                if message:
                    print(f"服务器端发送消息为: {message}")
                    if message == "pong":
                        print("服务器端发送消息为pong")
                    else:
                        print('服务器端发送消息不为pong')
                time.sleep(0.1)  # 避免过度占用 CPU
                
        print(f"尝试重连 {config.WEBSOCKET_RETRY_INTERVAL} seconds...")
        time.sleep(config.WEBSOCKET_RETRY_INTERVAL)


if __name__ == '__main__':
    main()