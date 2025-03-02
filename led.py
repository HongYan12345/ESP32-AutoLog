import machine
import time

# 初始化 LED 引脚
led = machine.Pin(2, machine.Pin.OUT)

def flash_led():
    led.value(1)  # 打开 LED
    time.sleep(1)  # 等待 1 秒
    led.value(0)  # 关闭 LED
    time.sleep(1)
# 点亮 LED
while True:
    flash_led()
      # 等待 1 秒