import network
import time

# 设置 WiFi 网络名称和密码
ssid = 'SIfar-2.4G'  # 替换为你的 WiFi 名称
password = 'SIfar.5858'  # 替换为你的 WiFi 密码

# 创建一个 WLAN 接口对象
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