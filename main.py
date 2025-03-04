import util_uart
import util_web
import config
import time
from machine import UART, Pin

#初始化串口
uart = UART(2, 115200)

# 全局变量，用于控制线程是否停止
stop_threads = False

# 初始化 LED
led = Pin(2, Pin.OUT)

# LED 闪烁函数
def flash_led():
    led.value(1)  # 打开 LED
    # time.sleep(0.1)  # 短暂点亮
    # led.value(0)  # 关闭 LED

# 使用示例
def print_message(message):
    """打印消息的回调函数"""
    print(message, end='')
    
def save_to_file(message):
    """保存到文件的回调函数"""
    with open('log.txt', 'a') as f:
        f.write(message + '\n')
        

class MessageHandler:
    def __init__(self, client: util_web.WebSocketClient):
        self.ws_client = client
        
    def print_message(self, message):
        """打印消息的回调函数"""
        #print(message, end='\n')
    
    def send_to_websocket(self, message):
        """发送到WebSocket服务器的回调函数"""
        
        if self.ws_client and self.ws_client.connected:
            if self.ws_client.send(message + '\n'):
                print(message, end='\n')
            else:
                print("发送失败")
        else:
            print("异常错误")

# 主程序
def main():
    global stop_threads
    #start_memory_cleaner(interval=10)
    
    # 连接 WiFi
    util_web.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD)
    ws_client = util_web.WebSocketClient(config.SERVER_HOST, config.SERVER_PORT)
    ws_client.connect()
    while ws_client.connected == False:
        print(f"尝试重连 {config.WEBSOCKET_RETRY_INTERVAL} seconds...")
        time.sleep(config.WEBSOCKET_RETRY_INTERVAL)
        ws_client.connect()

    # 创建消息处理器
    message_handler = MessageHandler(ws_client)
    
    # 创建日志读取器
    log_reader = util_uart.LogReader(config.UART_TX, config.UART_RX)
    
    # 添加回调函数
    log_reader.add_callback(message_handler.print_message)
    log_reader.add_callback(message_handler.send_to_websocket)
    
    # 开始读取日志
    log_reader.read_log()
    
    
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Main thread interrupted")
    finally:
        time.sleep(1)  # 等待线程关闭

    print("All threads stopped")



