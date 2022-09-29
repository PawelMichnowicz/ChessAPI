import functools
import websockets
import asyncio

from chess import Game

PORT = 5050


# ogranicz liczbe graczy do dwóch
connected = dict()

async def main(websocket, game):
    print("Connected")
    if not game.id in connected:
        connected[game.id] = [websocket,]
    else:
        connected[game.id].append(websocket)

    while len(connected[game.id]) < 2:
        print("Waiting for second player")
        await asyncio.sleep(0.5)

    player_1, player_2 = list(connected[game.id])[0], list(connected[game.id])[1]
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

        for conn in connected[game.id]:
            if conn != websocket:
                chessboard = game.get_chessboard(conn)
                await conn.send(f"Opponent's made {message}" + '\n' + chessboard)




async def create_game(websocket):

    game_id = await websocket.recv()
    game = Game.get(game_id)
    if not game:
        game = Game(game_id)
    else:
        game = game[0]
    return game


async def handler(websocket):

    game = await create_game(websocket)
    await main(websocket, game=game)



async def start_server():
    print('Server started')
    async with websockets.serve(
            handler,
            '0.0.0.0',
            PORT,
            ping_interval=None):
        await asyncio.Future()


asyncio.run(start_server())
