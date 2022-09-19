from sqlite3 import connect
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

    player_2, player_1 = list(connected)[0], list(connected)[1]
    game = Game(player_2, player_1)
    await websocket.send(str(websocket==player_1))

    async for message in websocket:
        try:
            (x,y), (xx,yy) = (message).split(':')
            start_pos = (int(x),int(y))
            end_pos = (int(xx),int(yy))
            game.handle_move(start_pos, end_pos, websocket)
            await websocket.send('ok')
        except Exception as e:
            await websocket.send(str(e))
            continue

        game.board.print_board()

        for conn in connected:
            if conn != websocket:
                await conn.send("Opponent made move")

async def start_server():
    print('Server started')
    async with websockets.serve(main, 'localhost', PORT, ping_interval=None):
        await asyncio.Future()


asyncio.run(start_server())

