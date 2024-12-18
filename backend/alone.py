import asyncio
import websockets
import random
import json

connected_clients = {}


async def client(cli, key):
    if key == "":
        return

    key = int(key)
    if key in connected_clients.keys():
        # 检查client是否已连接
        if connected_clients[key][1] != None:
            msg = json.dumps(
                {
                    "action": "key_err",
                    "params": "occupied",
                }
            )
            await cli.send(msg)
            await cli.close()
            return

        # 添加会话
        host = connected_clients[key][0]
        connected_clients[key][1] = cli
        # 发送问候语给client
        msg = json.dumps(
            {
                "action": "online_stat",
                "params": True,
            }
        )
        await cli.send(msg)
        # 发送问候语给host
        msg = json.dumps(
            {
                "action": "online_stat",
                "params": True,
            }
        )
        await host.send(msg)
        print(connected_clients)

        try:
            # 处理Session消息
            async for message in cli:
                data = json.loads(message)
                print(data)
                # 广播消息给所有连接的客户端
                await connected_clients[key][0].send(message)
                # await connected_clients[key][1].send(message)
        finally:
            msg = json.dumps(
                {
                    "action": "online_stat",
                    "params": False,
                }
            )
            if key in connected_clients.keys():
                await connected_clients[key][0].send(msg)
                connected_clients[key][1] = None
            print(connected_clients)

    else:
        msg = json.dumps(
            {
                "action": "key_err",
                "params": "error",
            }
        )
        await cli.send(msg)
        await cli.close()


async def host(websocket, path):
    # 生成ID
    key = random.randint(1000, 9999)
    # 去重
    while key in connected_clients:
        key = random.randint(1000, 9999)
    # 添加会话
    connected_clients[key] = [websocket, None]
    print(connected_clients)
    # 发送问候语
    msg = json.dumps(
        {
            "action": "init_id",
            "params": key,
        }
    )
    await websocket.send(msg)

    try:
        # 处理Session消息
        async for message in websocket:
            data = json.loads(message)
            print(data)
            # 广播消息给客户端
            # await connected_clients[key][0].send(message)
            if connected_clients[key][1]:
                await connected_clients[key][1].send(message)
    finally:
        msg = json.dumps(
            {
                "action": "online_stat",
                "params": False,
            }
        )
        if connected_clients[key][1]:
            await connected_clients[key][1].send(msg)
            await connected_clients[key][1].close()

        # Unregister
        del connected_clients[key]
        print(connected_clients)


async def handler(websocket, path):
    if path == "/host":
        await host(websocket, path)
    elif path[:7] == "/client":
        key = path[8:]
        await client(websocket, key)
    else:
        await websocket.close()


# start_server = websockets.serve(handler, None, 9001)
#
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()


async def main():
    async with websockets.serve(handler, None, 9001):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
