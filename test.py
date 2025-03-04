import network
import time
import socket
import json
import config

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

class SocketIOClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.sid = None
        
    def _handshake(self):
        # 首先进行 Engine.IO 握手
        s = socket.socket()
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        s.connect(addr)
        
        # 发送 HTTP GET 请求进行握手
        request = (
            f"GET /socket.io/?EIO=4&transport=polling HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Connection: close\r\n\r\n"
        )
        s.send(request.encode())
        
        # 读取响应
        response = ''
        while True:
            data = s.recv(1024).decode()
            if not data:
                break
            response += data
            
        print("握手响应:", response)
        s.close()
        return True
        
    def connect(self):
        try:
            if self._handshake():
                self.socket = socket.socket()
                addr = socket.getaddrinfo(self.host, self.port)[0][-1]
                self.socket.connect(addr)
                print("WebSocket 连接已建立")
                return True
        except Exception as e:
            print("连接错误:", str(e))
            return False
            
    def emit(self, event, data):
        try:
            message = f'42{json.dumps([event, data])}'
            self.socket.send(message.encode())
            return True
        except Exception as e:
            print("发送错误:", str(e))
            return False
            
    def receive(self):
        try:
            data = self.socket.recv(1024).decode()
            if data.startswith('42'):
                return json.loads(data[2:])
            return None
        except Exception as e:
            print("接收错误:", str(e))
            return None
            
    def close(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

def websocket_client():
    print('正在连接到SocketIO服务器...')
    client = SocketIOClient(config.WS_HOST, config.WS_PORT)
    
    try:
        if client.connect():
            while True:
                # 发送消息
                if client.emit('message', 'Hello from ESP32!'):
                    print('消息已发送')
                
                # 接收消息
                msg = client.receive()
                if msg:
                    print('收到消息:', msg)
                
                time.sleep(config.WEBSOCKET_RETRY_INTERVAL)
    except Exception as e:
        print('发生错误:', str(e))
    finally:
        client.close()

def main():
    connect_wifi()
    websocket_client()

if __name__ == '__main__':
    main()