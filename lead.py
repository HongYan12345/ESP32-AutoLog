import time
from machine import UART, Pin
import machine

uart = UART(2,115200)
# 初始化 UART2
#配置 TX和 RX引脚
uart.init(tx=16,rx=17)


def read_log():
  print("开始读取设备 log...")
  while True:
    if uart.any():
#读取所有可用数据
      data = uart.read(uart.any())
      try:
# 尝试使用 UTF-8 解码
        print(data.decode('utf-8'),end='')
      except UnicodeError:
#如果 UTF-8 解码失败，尝试使用 IS0-8859-1 解码
        print(data.decode('iso-8859-1'),end='')
    time.sleep(0.1)#每次循环暂停 0.1 秒，减少 CPU 使用
# 主程序

read_log()