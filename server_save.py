import asyncio
import json

import requests
import websockets

from chess import Game
from utils import send_response_to_opponent, send_response_to_player

PORT = 5050
QUERY_GET_CHALLANGE = 'query {{challange (gameId: "{}"){{id fromUser {{username}} toUser {{username}} }} }}'
URL = "http://app:8000/graphql"


connected_users = dict()

# szewczyk e2:e3 , d1:f3, f1:c4, f3:f7
async def main(websocket, game, username):

    if not game.id in connected_users:
        connected_users[game.id] = [{"username": username, "websocket": websocket}]
    else:
        connected_users[game.id].append({"username": username, "websocket": websocket})

    while len(connected_users[game.id]) < 2:
        print("Waiting for second player")
        await asyncio.sleep(0.5)

    # Assign websockets to players and choose which one starts first move
    player_1, player_2 = connected_users[game.id][0], connected_users[game.id][1]
    game.place_players(player_1, player_2)
    await websocket.send(str(websocket == player_1["websocket"]))

    async for message in websocket:


        if message == "give up":
            if str(websocket == player_1["websocket"]):
                winner = game.player_1
            else:
                winner = game.player_2
            game.end_with_win(winner, f"{winner.username} won! Opponent gave up... ")
            await user["websocket"].send("end_game")

        elif message == "draw":
            for user in connected_users[game.id]:
                if user["websocket"] != websocket:
                    await user["websocket"].send("draw offer")

        elif message == "Y":
            game.end_with_draw('Draw by mutal consent')
            await user["websocket"].send("end_game")

        elif message =="N":
            for user in connected_users[game.id]:
                if user["websocket"] != websocket:
                    await user["websocket"].send("Odrzucono")

        else:
            try:
                start_field, end_field = (message).split(":")
                game.handle_move(start_field, end_field, websocket)
                for user in connected_users[game.id]:
                    if user["websocket"] != websocket:
                        await user["websocket"].send("made ruch")

            except Exception as error:
                await websocket.send("Try again \n" + str(error))
                continue


        # sending board
        for user in connected_users[game.id]:
            if user["websocket"] != websocket:
                await user["websocket"].send(game.get_chessboard(websocket))
        await websocket.send(game.get_chessboard(websocket))


        if game.is_over:
            break


async def create_game(websocket):
    while True:
        try:
            game_id = await websocket.recv()
            query = QUERY_GET_CHALLANGE.format(game_id)
            response = requests.post(url=URL, json={"query": query})
            json_data = json.loads(response.text)
            if not json_data["data"]["challange"]:
                raise Exception("Game with this id doesn't exists")
            await websocket.send("id_ok")

            username = await websocket.recv()
            if (
                json_data["data"]["challange"]["fromUser"]["username"] != username
                and json_data["data"]["challange"]["toUser"]["username"] != username
            ):
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
        game = game[0]
    return game, username


async def handler(websocket):
    game, username = await create_game(websocket)
    await main(websocket, game=game, username=username)


async def start_server():
    print("Server started")
    async with websockets.serve(handler, "0.0.0.0", PORT, ping_interval=None):
        await asyncio.Future()


asyncio.run(start_server())
