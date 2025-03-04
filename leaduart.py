import time
import network
from machine import UART, Pin
import ntptime  # 用于从网络获取时间
import gc  # 引入垃圾回收模块
import _thread

#初始化串口
uart = UART(2, 115200)

# 全局变量，用于控制线程是否停止
stop_threads = False

# 初始化 LED
led = Pin(2, Pin.OUT)

# WiFi 配置
WIFI_SSID = "SIfar-2.4G"
WIFI_PASSWORD = "SIfar.5858"


# 初始化 UART2
def initialize_uart():
    global uart
    try:
        uart.init(tx=16, rx=17)
        print("UART initialized successfully.")
    except Exception as e:
        print("Failed to initialize UART:", e)

# 连接 WiFi
def connect_wifi():
    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # 等待连接
    while not wlan.isconnected():
        time.sleep(1)
        print("Wifi Connecting...")
    
    print("Connected to WiFi!")
    print("IP Address:", wlan.ifconfig()[0])

# 从网络获取时间
def sync_time():
    print("Syncing time from NTP server...")
    try:
        ntptime.host = "pool.ntp.org"  # NTP 服务器地址
        ntptime.settime()  # 设置系统时间
        print("Time synced!")
    except Exception as e:
        print("Failed to sync time:", e)

# 生成时间戳
def get_timestamp():
    t = time.localtime()  # 获取秒级时间
    ticks = time.ticks_us()  # 获取微秒级时间戳（从程序启动开始计时）
    microsecond = ticks % 1_000_000  # 取出微秒部分
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:06d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5], microsecond
    )

# LED 闪烁函数
def flash_led():
    led.value(1)  # 打开 LED
    # time.sleep(0.1)  # 短暂点亮
    # led.value(0)  # 关闭 LED

# 读取日志并打印
def read_log():
    initialize_uart()
    print("Start reading log...")
    buffer = b""  # 使用字节缓冲区
    while True:
        try:
            available = uart.any()
            if available:
                data = uart.read(available)  # 读取所有可用数据
                if data:
                    buffer += data
                    flash_led()
                    
                    # 处理缓冲区中的数据
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        try:
                            decoded_line = line.decode('utf-8')
                            print(f"[{get_timestamp()}] {decoded_line}\n", end='')
                        except UnicodeError:
                            decoded_line = line.decode('iso-8859-1')
                            print(f"[{get_timestamp()}] {decoded_line}\n", end='')
            else:
                # 处理剩余的缓冲区数据（如果没有完整的行）
                if buffer:
                    try:
                        decoded_line = buffer.decode('utf-8')
                        print(f"[{get_timestamp()}] {decoded_line}\n", end='')
                    except UnicodeError:
                        decoded_line = buffer.decode('iso-8859-1')
                        print(f"[{get_timestamp()}] {decoded_line}\n", end='')
                    buffer = b""

            time.sleep(0.1)  # 避免过度占用 CPU
        except Exception as e:
            print("Error reading UART:", e)
            print("Attempting to reconnect...")
            time.sleep(1)
            continue
        

def mem_free():
    gc.collect() # 执行垃圾回收
    free_memory_bytes = gc.mem_free()
# 转换为 KB 和 MB
    free_memory_kb = free_memory_bytes / 1024
    free_memory_mb = free_memory_kb / 1024

    print("Free memory: {:.2f} KB = {:.2f} MB".format(free_memory_kb, free_memory_mb))


# 线程函数：定期清理内存
def memory_cleaner_thread(interval=10):
    global stop_threads
    while not stop_threads:
        print("Allocated memory:", gc.mem_alloc()/1024, "KB")
        mem_free()
        time.sleep(interval)  # 等待指定的时间间隔
    print("cleaner thread finish...")

# 启动内存清理线程
def start_memory_cleaner(interval=10):
    global stop_threads
    stop_threads = False  # 确保线程可以正常启动
    _thread.start_new_thread(memory_cleaner_thread, (interval,))

# 停止内存清理线程
def stop_memory_cleaner():
    global stop_threads
    stop_threads = True  # 设置标志位为True，通知线程停止运行


# 主程序
def main():
    global stop_threads
    #start_memory_cleaner(interval=10)
    
    # 连接 WiFi
    connect_wifi()
    
    # 同步时间
    sync_time()
    
    # 开始读取日志
    read_log()

# 运行主程序
try:
    main()
except KeyboardInterrupt:
    print("Main thread interrupted")
finally:
    stop_memory_cleaner()
    time.sleep(1)  # 等待线程关闭

print("All threads stopped")