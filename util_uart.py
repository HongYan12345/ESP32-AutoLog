import time
from machine import UART, Pin
import config
import util_command

uart = UART(2, 115200)

# 初始化 UART2
def initialize_uart(uart_tx, uart_rx):
    global uart
    try:
        uart.init(tx=uart_tx, rx=uart_rx)
        print("UART initialized successfully.")
    except Exception as e:
        print("Failed to initialize UART:", e)

# 生成时间戳
def get_timestamp():
    t = time.localtime()  # 获取秒级时间
    ticks = time.ticks_us()  # 获取微秒级时间戳（从程序启动开始计时）
    microsecond = ticks % 1_000_000  # 取出微秒部分
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:06d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5], microsecond
    )


class LogReader:
    def __init__(self, uart_tx, uart_rx):
        self.buffer = b""
        self.callbacks = []
        self.cmd_manager = util_command.CommandManager()
        initialize_uart(uart_tx, uart_rx)
        
    def add_callback(self, callback):
        """添加消息处理回调函数"""
        self.callbacks.append(callback)
        
    def notify_callbacks(self, message):
        """触发所有回调函数"""
        for callback in self.callbacks:
            callback(message)
            
    def process_buffer(self):
        """处理缓冲区数据"""
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            try:
                decoded_line = line.decode('utf-8')
            except UnicodeError:
                decoded_line = line.decode('iso-8859-1')
                
            timestamp_message = f"[{get_timestamp()}] {decoded_line}"
            self.notify_callbacks(timestamp_message)
            
    def read_log(self):
        """读取并处理日志"""
        print("Start reading log...")
        while True:
            try:
                available = uart.any()
                if available:
                    data = uart.read(available)
                    if data:
                        self.buffer += data
                        self.process_buffer()
                else:
                    # 处理剩余的缓冲区数据
                    if self.buffer:
                        try:
                            decoded_line = self.buffer.decode('utf-8')
                        except UnicodeError:
                            decoded_line = self.buffer.decode('iso-8859-1')
                            
                        timestamp_message = f"[LOG_CAM][{get_timestamp()}] {decoded_line}"
                        self.notify_callbacks(timestamp_message)
                        self.buffer = b""

                time.sleep(0.1)
                
            except Exception as e:
                print("Error reading UART:", e)
                print("Attempting to reconnect...")
                time.sleep(1)
                continue
    def write_command(self, command):
        """
        向串口写入命令
        command: 要发送的命令字符串
        return: True表示发送成功，False表示发送失败
        """
        try:
            if isinstance(command, str):
                command = command.encode('utf-8')
            
            if not command.endswith(b'\n'):
                command += b'\n'
                
            uart.write(command)
            return True
        except Exception as e:
            print("串口写入错误:", e)
            return False
            
    def write_command_with_response(self, command, timeout=1.0):
        """
        发送命令并等待响应
        command: 要发送的命令
        timeout: 等待响应的超时时间（秒）
        return: 返回收到的响应，超时或错误返回None
        """
        if not self.write_command(command):
            return None
            
        start_time = time.time()
        response = b""
        
        while (time.time() - start_time) < timeout:
            if uart.any():
                data = uart.read()
                if data:
                    response += data
                    if b'\n' in response:  # 收到完整行
                        try:
                            return response.decode('utf-8').strip()
                        except UnicodeError:
                            return response.decode('iso-8859-1').strip()
            time.sleep(0.01)
            
        return None
            
    def execute_command(self, command_key, timeout=1.0):
        """执行指令"""
        command = self.cmd_manager.get_command(command_key)
        if not command:
            print(f"未知指令: {command_key}")
            return None
        print(f"执行指令: {command_key}")
        return self.write_command_with_response(command, timeout)
        
    def update_commands(self, new_commands):
        """更新指令集"""
        self.cmd_manager.update_from_server(new_commands)

# 使用示例
def print_message(message):
    """打印消息的回调函数"""
    print(message, end='\n')
    
def save_to_file(message):
    """保存到文件的回调函数"""
    with open('log.txt', 'a') as f:
        f.write(message + '\n')

# 创建并启动日志读取器
def start_log_reader():
    log_reader = LogReader(config.UART_TX, config.UART_RX)
    # 添加回调函数
    #log_reader.add_callback(print_message)
    #log_reader.add_callback(save_to_file)
    # 开始读取日志
    #log_reader.read_log()
    print(log_reader.execute_command('help'))

if __name__ == '__main__':
    start_log_reader()