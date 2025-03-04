import network
import time
import json
import socket
import config
from machine import Timer
import ntptime  # 用于从网络获取时间
import random


def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('连接到WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('WiFi已连接')
    print('IP地址:', wlan.ifconfig()[0])
    # 同步时间
    print('开始同步时间')
    sync_time()

# 从网络获取时间
def sync_time():
    print("正在从ntp服务器获取时间...")
    try:
        ntptime.host = "pool.ntp.org"  # NTP 服务器地址
        ntptime.settime()  # 设置系统时间
        print("时间同步成功!")
    except Exception as e:
        print("时间同步失败:", e)


class WebSocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.last_send_time = 0
        self.min_send_interval = 0.5
        self.max_queue_size = 100
        self.message_queue = config.BoundedQueue(self.max_queue_size)
        
    def connect(self):
        try:
            print("开始连接服务器")
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
            
        current_time = time.time()
        should_send = (
            current_time - self.last_send_time >= self.min_send_interval or  # 时间到了
            len(self.message_queue) >= self.max_queue_size - 1  # 队列快满了
        )
        
        if should_send:
            # 先发送队列中的消息
            success = self._send_queued_messages()
            if not success:
                return False
            # 直接发送当前消息
            return self._send_single_message(message, is_binary)
        else:
            # 加入队列
            self.message_queue.append((message, is_binary))
            return True
        
    def _send_queued_messages(self):
        """发送队列中的所有消息"""
        if not self.message_queue:
            return True
            
        print(f"发送队列中的 {len(self.message_queue)} 条消息")
        while self.message_queue:
            msg, is_binary = self.message_queue.popleft()
            if not self._send_single_message(msg, is_binary):
                # 发送失败，将未发送的消息放回队列
                self.message_queue.appendleft((msg, is_binary))
                return False
        return True
        
    def _send_single_message(self, message, is_binary):
        try:
            # 准备数据
            if isinstance(message, str):
                payload = message.encode('utf-8')
            else:
                payload = message
            
            # 生成随机掩码
            mask = bytearray([
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ])
        
            # 应用掩码到数据
            masked_payload = bytearray(len(payload))
            for i in range(len(payload)):
                masked_payload[i] = payload[i] ^ mask[i % 4]
            
            # 构建帧头
            length = len(payload)
            frame = bytearray()
            frame.append(0x81 if not is_binary else 0x82)
        
            if length < 126:
                frame.append(0x80 | length)
            elif length < 65536:
                frame.append(0x80 | 126)
                frame.extend(length.to_bytes(2, 'big'))
            else:
                frame.append(0x80 | 127)
                frame.extend(length.to_bytes(8, 'big'))
            
            frame.extend(mask)
            frame.extend(masked_payload)
        
            # 分块发送大数据
            chunk_size = 512
            for i in range(0, len(frame), chunk_size):
                chunk = frame[i:i + chunk_size]
                self.socket.send(chunk)
                time.sleep(0.01)  # 小延时让数据发送完成
            
            self.last_send_time = time.time()
            return True
        
        except Exception as e:
            print(f"发送失败: {str(e)}")
            self.close()
            return False
            
    def check_and_send_queue(self):
        """检查是否可以发送队列中的消息"""
        if not self.message_queue:
            return True
            
        current_time = time.time()
        if current_time - self.last_send_time >= self.min_send_interval:
            return self._send_queued_messages()
        return True
            
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
            
            # 读取掩码（如果有的话）
            mask = None
            if header[1] & 0x80:
                mask = self.socket.recv(4)
                
            # 读取数据
            data = self.socket.recv(length)
            
            # 如果有掩码，解码数据
            if mask:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
                
            # 根据opcode处理数据
            if opcode == 0x1:  # 文本数据
                return data.decode('utf-8')
            elif opcode == 0x2:  # 二进制数据
                return data
            else:
                return None
            
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
    connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD)
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
                    print(f"服务器端接收: {message}")
                time.sleep(0.1)  # 避免过度占用 CPU
                
        print(f"尝试重连 {config.WEBSOCKET_RETRY_INTERVAL} seconds...")
        time.sleep(config.WEBSOCKET_RETRY_INTERVAL)


if __name__ == '__main__':
    main()

