

import asyncio
import websockets

async def test_websocket():
    uri = "ws://18.166.245.229:6789"  # 替换为你的 WebSocket 服务器地址
    async with websockets.connect(uri) as websocket:
        # 发送消息
        await websocket.send("Hello from client!")
        print("Sent message: Hello from client!")
        
        # 接收消息
        response = await websocket.recv()
        print(f"Received response: {response}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
