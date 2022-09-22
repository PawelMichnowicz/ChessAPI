import functools
import websockets
import asyncio

from chess import Game

PORT = 5050

connected = set()

# ogranicz liczbe graczy do dwóch
# popraw waiting for sec... -> niech idzie do gracza


async def main(websocket, path, game):
    print("Connected")
    connected.add(websocket)

    while len(connected) < 2:
        print("Waiting for second player")
        await asyncio.sleep(0.5)

    player_1, player_2 = list(connected)[0], list(connected)[1]
    game.place_players(player_1, player_2)
    await websocket.send(str(websocket == player_1))

    async for message in websocket:
        try:
            start_field, end_field = (message).split(':')
            game.handle_move(start_field, end_field, websocket)
        except Exception as e:
            await websocket.send(str(e))
            continue
        await websocket.send('ok')
        await websocket.send(game.get_chessboard(websocket))

        for conn in connected:
            if conn != websocket:
                chessboard = game.get_chessboard(conn)
                await conn.send(f"Opponent's made {message}" + '\n' + chessboard)


async def start_server():
    print('Server started')
    game = Game()
    async with websockets.serve(
            functools.partial(main, game=game),
            'localhost',
            PORT,
            ping_interval=None):
        await asyncio.Future()


asyncio.run(start_server())
