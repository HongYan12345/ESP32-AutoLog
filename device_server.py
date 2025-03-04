import asyncio
import websockets

async def send_message(uri: str, message: str):
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket server at {uri}")

            # 发送消息到服务器
            await websocket.send(message)
            print(f"Sent message: {message}")

            # 等待服务器的回复
            response = await websocket.recv()
            print(f"Received message: {response}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

# 替换为您的WebSocket服务器地址
SERVER_URI = "ws://18.166.245.229:6789"
MESSAGE = "Hello, WebSocket Server!"

# 运行异步函数
asyncio.get_event_loop().run_until_complete(send_message(SERVER_URI, MESSAGE))
