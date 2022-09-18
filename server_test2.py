import websockets
import asyncio
import itertools

from chess import Game, BLACK, WHITE
PORT = 5050

connected = set()

# ogranicz liczbe graczy do dwóch
# popraw waiting -> niech idzie do gracza


async def main(websocket, path):
    print("Connected")
    connected.add(websocket)

    while len(connected)<2:
        print("Waiting for second player")
        await asyncio.sleep(1)

    # player_1, player_2 = list(connected)[0], list(connected)[1]
    # await websocket.send(str(websocket==player_1))


    async for message in websocket:

        await websocket.send(message)

        for conn in connected:
            if conn != websocket:
                await conn.send("Opponent's move: " + message )

async def start_server():
    print('Server started')
    async with websockets.serve(main, 'localhost', PORT, ping_interval=None):
        await asyncio.Future()


asyncio.run(start_server())
