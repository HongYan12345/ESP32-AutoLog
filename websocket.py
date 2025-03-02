import network
import time
from machine import UART
import websocket_helper  # 需要提前安装 MicroPython 的 WebSocket 库

# 配置部分
WIFI_SSID = "SIfar-2.4G"
WIFI_PASSWORD = "SIfar.5858"
WS_SERVER_URL = "http://18.166.245.229:6789"  # WebSocket 服务器地址

# 初始化串口（UART2，根据引脚调整）
uart = UART(2, baudrate=115200)
uart.init(tx=17, rx=16, timeout=1000)

# 连接 Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Wi-Fi Connected. IP:", wlan.ifconfig()[0])

# 主函数：读取串口数据并通过 WebSocket 发送
def main():
    connect_wifi()
    ws = None
    while True:
        try:
            # 初始化 WebSocket 连接
            if not ws:
                print("Connecting to WebSocket...")
                ws = websocket_helper.WebSocket()
                ws.connect(WS_SERVER_URL)
                print("WebSocket Connected")
                message = {'data': 'Hello from client!'}
                ws.send(message)
                #ws.send({'data': 'Hello from client!'})
                response = ws.recv()
                print(f"Received response: {response}")
            # # 读取串口数据并发送
            # if uart.any():
            #     data = uart.read(uart.any())  # 读取所有可用数据
            #     try:
            #         decoded_data = data.decode('utf-8')  # 尝试 UTF-8 解码
            #     except UnicodeError:
            #         decoded_data = data.decode('iso-8859-1', errors='replace')  # 兼容性解码
            #     print("[UART]", decoded_data, end='')
            #     ws.send(decoded_data)  # 发送数据到服务器

        except Exception as e:
            print("Error:", e)
            if ws:
                ws.close()
                ws = None
            time.sleep(5)  # 等待后重连
        time.sleep(0.1)  # 降低 CPU 占用

if __name__ == "__main__":
    main()