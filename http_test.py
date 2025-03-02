import network
import time
from machine import UART
import urequests  # MicroPython 的 HTTP 请求库
import gc  # 引入垃圾回收模块


# 配置部分
WIFI_SSID = "SIfar-2.4G"
WIFI_PASSWORD = "SIfar.5858"
HTTP_SERVER_URL = "https://test-htcs.wuyuantech.com/user/actuator"  # HTTP 服务器地址

# 初始化串口（UART2，根据引脚调整）
uart = UART(2, baudrate=115200)
uart.init(tx=17, rx=16, timeout=1000)

def mem_free():
    gc.collect()
    free_memory_bytes = gc.mem_free()
# 转换为 KB 和 MB
    free_memory_kb = free_memory_bytes / 1024
    free_memory_mb = free_memory_kb / 1024

    print("Free memory: {} bytes".format(free_memory_bytes))
    print("Free memory: {:.2f} KB".format(free_memory_kb))
    print("Free memory: {:.2f} MB".format(free_memory_mb))

# 连接 Wi-Fi
def connect_wifi(ssid, password):
  wlan = network.WLAN(network.STA_IF)
  # 启用 WLAN 接口
  wlan.active(True)

  # 连接到指定的 WiFi 网络
  print('Connecting to WiFi...')
  wlan.connect(ssid, password)

  # 等待连接成功
  while not wlan.isconnected():
      print('Waiting for connection...')
      time.sleep(1)

  # 打印连接成功的信息
  print('Connected to WiFi!')
  print('Network config:', wlan.ifconfig())

def send_get(url):
    print('start get...', url)
    response = urequests.post(HTTP_SERVER_URL, data=url)
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.text)  # 打印响应的文本内容
    response.close()

# 主函数：读取串口数据并通过 HTTP 发送
def main():
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    mem_free()
    send_get(HTTP_SERVER_URL)
    # while True:
    #     try:
    #         # 读取串口数据并发送
    #         if uart.any():
    #             data = uart.read(uart.any())  # 读取所有可用数据
    #             try:
    #                 decoded_data = data.decode('utf-8')  # 尝试 UTF-8 解码
    #             except UnicodeError:
    #                 decoded_data = data.decode('iso-8859-1', errors='replace')  # 兼容性解码
    #             print("[UART]", decoded_data, end='')

    #             # 发送 HTTP POST 请求
    #             response = urequests.post(HTTP_SERVER_URL, data=decoded_data)
    #             if response.status_code == 200:
    #                 print("Data sent successfully")
    #             else:
    #                 print("Failed to send data, status code:", response.status_code)
    #             response.close()

    #     except Exception as e:
    #         print("Error:", e)
    #         time.sleep(5)  # 等待后重试
    #     time.sleep(0.1)  # 降低 CPU 占用

if __name__ == "__main__":
    main()