import websockets
import asyncio
import requests
import json
from chess import Game



PORT = 5050
QUERY_GET_CHALLANGE = 'query {{challange (gameId: "{}"){{id fromPlayer {{username}} toPlayer {{username}} }} }}'
URL = 'http://app:8000/graphql'


connected = dict()

async def main(websocket, game, username):
    print("Connected")
    if not game.id in connected:
        connected[game.id] = [{'username':username, 'websocket':websocket}]
    else:
        connected[game.id].append({'username':username, 'websocket':websocket})

    while len(connected[game.id]) < 2:
        print("Waiting for second player")
        await asyncio.sleep(0.5)

    player_1, player_2 = connected[game.id][0], connected[game.id][1]
    game.place_players(player_1, player_2)

    await websocket.send(str(websocket == player_1['websocket']))

    async for message in websocket:
        try:
            start_field, end_field = (message).split(':')
            game.handle_move(start_field, end_field, websocket)
        except Exception as error:
            if str(error) == 'Check-mate':
                game.end_with_win(websocket)
                await websocket.send('Check-mate')
                await websocket.send(game.get_chessboard(websocket))
                for conn in connected[game.id]:
                    if conn['websocket'] != websocket:
                        await conn['websocket'].send('end_game')
                        await conn['websocket'].send(game.get_chessboard(websocket))
                break
            else: # incorrect move
                await websocket.send(str(error))
                continue
        await websocket.send('ok')
        await websocket.send(game.get_chessboard(websocket))

        for conn in connected[game.id]:
            if conn['websocket'] != websocket:
                chessboard = game.get_chessboard(conn['websocket'])
                await conn['websocket'].send(f"Opponent's made {message}" + '\n' + chessboard)


    for connection in connected[game.id]:
        if game.winner:
            await connection['websocket'].send(f'Game over! Winner:{game.winner.username}')
        else:
            await connection['websocket'].send('Game over! There is a stalemate')




# szewczyk e2:e3 , d1:f3, f1:c4, f3:f7
# a7:a6...

# f2:f4, g2:g4
# e7:e6, d8:h4


async def create_game(websocket):

    while True:
        try:
            game_id = await websocket.recv()
            query = QUERY_GET_CHALLANGE.format(game_id)
            response = requests.post(url=URL, json={'query': query})
            json_data = json.loads(response.text)
            if not json_data['data']['challange']:
                raise Exception("Game with this id doesn't exists")
            await websocket.send("id_ok")

            username = await websocket.recv()
            if json_data['data']['challange']['fromPlayer']['username'] != username and json_data['data']['challange']['toPlayer']['username'] != username:
                raise Exception("You are not involved into this game")
            await websocket.send("username_ok")
            break
        except Exception as e:
                await websocket.send(str(e))
                continue

    game = Game.get(game_id)
    if not game:
        game = Game(game_id)
    else:
        game = game[0] # popraw sprawdź czy można bez
    return game, username


async def handler(websocket):

    game, username = await create_game(websocket)
    await main(websocket, game=game, username=username)



async def start_server():
    print('Server started')
    async with websockets.serve(
            handler,
            '0.0.0.0',
            PORT,
            ping_interval=None):
        await asyncio.Future()


asyncio.run(start_server())
