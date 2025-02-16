import asyncio
import json
# import websockets
from websockets.asyncio.server import serve

socket_server_port = 12345
websocket_server_port = 8765

ws_clients = set()


class UDPServerProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        message = data.decode("utf-8").strip()
        print(f"Received UDP data from {addr}: {message}")

        parts = message.split(',')
        if len(parts) < 3:
            print("Invalid UDP data:", message)
            return

        try:
            timestamp = parts[0]
            x = float(parts[1])
            y = float(parts[2])
        except Exception as e:
            print("Error parsing UDP data:", e)
            return

        json_data = json.dumps({
            "timestamp": timestamp,
            "x": x,
            "y": y
        })

        asyncio.create_task(broadcast(json_data))


async def broadcast(message):
    if ws_clients:
        print("Broadcasting message:", message)
        await asyncio.gather(*(client.send(message) for client in ws_clients))
    else:
        print("No WebSocket clients connected.")


async def ws_handler(websocket):
    print("WebSocket client connected:", websocket.remote_address)
    ws_clients.add(websocket)

    try:
        async for _ in websocket:
            pass
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket client disconnected:", websocket.remote_address)
    finally:
        ws_clients.remove(websocket)


async def main():
    loop = asyncio.get_running_loop()

    print("Starting UDP server...")
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(),
        local_addr=("0.0.0.0", socket_server_port)
    )

    print("Starting WebSocket server...")
    async with serve(ws_handler, "localhost", websocket_server_port) as server:
        print(f"Servers running! UDP on port {socket_server_port}, WebSocket on port {websocket_server_port}")
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down the server")
