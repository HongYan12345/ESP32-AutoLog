from machine import Pin
import time

class ButtonManager:
    def __init__(self):
        # 使用字典存储按钮对象，键是按钮名称，值是对应的 Pin 对象
        self.buttons = {
            "button_menu": Pin(33, Pin.OUT),
            "button_ok": Pin(25, Pin.OUT),
            "button_down": Pin(2, Pin.OUT)
        }

    def click_button(self, button_name):
        # 确保按钮存在
        if button_name not in self.buttons:
            print(f"Button {button_name} not found!")
            return
        
        # 获取按钮对象
        btn = self.buttons[button_name]
        btn.value(1)  # 按下按钮
        print(f"Pressed {button_name}")
        time.sleep(0.1)
        btn.value(0)  # 释放按钮
        print(f"Released {button_name}")

# 初始化按钮管理器
button_manager = ButtonManager()

def main():
    while True:
        # 调用按钮
        button_manager.click_button("button_ok")
        time.sleep(1)
        button_manager.click_button("button_menu")
        time.sleep(1)  # 每次点击间隔 2 秒

if __name__ == '__main__':
    main()