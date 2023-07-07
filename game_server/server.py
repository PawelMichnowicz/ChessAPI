import asyncio
import json


import requests
import websockets

from chess import Game
from utils import send_response_to_opponent, send_response_to_player


import config


class ChessServer:
    def __init__(self) -> None:
        self.connected_users = {}

    async def create_game(self, websocket):
        while True:
            try:
                game_id = await websocket.recv()
                query = config.QUERY_GET_CHALLANGE.format(game_id)
                response = requests.post(url=config.URL, json={"query": query})
                json_data = json.loads(response.text)
                if not json_data["data"]["challange"]:
                    raise Exception("Game with this id doesn't exists")
                await websocket.send(config.MESSAGE_CORRECT_ID)

                username = await websocket.recv()
                if (
                    json_data["data"]["challange"]["fromUser"]["username"] != username
                    and json_data["data"]["challange"]["toUser"]["username"] != username
                ):
                    raise Exception("You are not involved into this game")
                await websocket.send(config.MESSAGE_CORRECT_USERNAME)
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

    async def log_in_to_game(self, websocket, game, username):
        if not game.id in self.connected_users:
            self.connected_users[game.id] = [
                {"username": username, "websocket": websocket}
            ]
        else:
            self.connected_users[game.id].append(
                {"username": username, "websocket": websocket}
            )

        while len(self.connected_users[game.id]) < 2:
            print("Waiting for second player")
            await asyncio.sleep(0.5)

        # Assign websockets to players and choose which one starts first move
        player_1, player_2 = (
            self.connected_users[game.id][0],
            self.connected_users[game.id][1],
        )
        game.place_players(player_1, player_2)
        await websocket.send(str(websocket == player_1["websocket"]))

    async def main(self, websocket, game):
        async for message in websocket:
            if message == config.COMMAND_DRAW_OFFER:
                # to both send offer
                for user in self.connected_users[game.id]:
                    if user["websocket"] != websocket:
                        await user["websocket"].send(config.MESSAGE_DRAW_OFFER)
                await websocket.send(config.MESSAGE_DRAW_OFFER)
                continue

            elif message == config.COMMAND_DRAW_DECLINED:
                for user in self.connected_users[game.id]:
                    if user["websocket"] != websocket:
                        await user["websocket"].send(config.MESSAGE_DRAW_DECLINED)
                continue

            elif message == config.COMMAND_DRAW_ACCEPTED:
                game.end_with_draw("Draw by mutal consent")
                for user in self.connected_users[game.id]:
                    if user["websocket"] != websocket:
                        await user["websocket"].send(config.MESSAGE_DRAW_ACCEPTED)
                await websocket.send(config.MESSAGE_DRAW_ACCEPTED)

            elif message == config.COMMAND_GIVE_UP:
                if str(websocket == game.player_1.websocket):
                    winner = game.player_1
                else:
                    winner = game.player_2
                game.end_with_win(
                    winner, f"{winner.username} won! Opponent gave up... "
                )
                await user["websocket"].send(config.MESSAGE_END_GAME)

            else:
                try:
                    start_field, end_field = (message).split(":")
                    game.handle_move(start_field, end_field, websocket)
                    for user in self.connected_users[game.id]:
                        if user["websocket"] != websocket:
                            await user["websocket"].send(config.MESSAGE_CORRECT_MOVE)
                    await websocket.send(config.MESSAGE_CORRECT_MOVE)

                except Exception as error:
                    await websocket.send(
                        config.MESSAGE_INCORRECT_MOVE + "\n" + str(error)
                    )
                    continue

            # sending board
            for user in self.connected_users[game.id]:
                if user["websocket"] != websocket:
                    await user["websocket"].send(game.get_chessboard(websocket))
            await websocket.send(game.get_chessboard(websocket))

            if game.is_over:
                break


async def handler(websocket):
    game, username = await server.create_game(websocket)
    await server.log_in_to_game(websocket, game, username)
    await server.main(websocket, game)


async def start_server():
    print("Server started")
    async with websockets.serve(handler, "0.0.0.0", config.PORT, ping_interval=None):
        await asyncio.Future()


if __name__ == "__main__":
    server = ChessServer()
    asyncio.run(start_server())
