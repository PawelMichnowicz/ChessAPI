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

    @staticmethod
    def get_current_player(websocket, game):
        if str(websocket == game.player_1.websocket):
            return game.player_1
        else:
            return game.player_2

    async def log_in_to_game(self, websocket):
        while True:
            try:
                game_id = await websocket.recv()
                query = config.QUERY_GET_CHALLANGE.format(game_id)
                response = requests.post(url=config.URL, json={"query": query})

                json_data = json.loads(response.text)
                print(json_data["data"]["challange"]["fromUser"]["eloRating"])
                print(type(json_data["data"]["challange"]["toUser"]["eloRating"]))

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

        # Collect data about user
        elo_rating_changes = json.loads(
            json_data["data"]["challange"]["eloRatingChanges"]
        )
        if json_data["data"]["challange"]["fromUser"]["username"] == username:
            elo_rating = json_data["data"]["challange"]["fromUser"]["eloRating"]
        else:
            elo_rating = json_data["data"]["challange"]["toUser"]["eloRating"]
        user = {
            "username": username,
            "elo_rating": elo_rating,
            "elo_rating_changes": elo_rating_changes[username],
            "websocket": websocket,
        }

        return game_id, user

    async def create_game(self, websocket, game_id, user):
        # Create instance of the game
        game = Game.get(game_id)
        if not game:
            game = Game(game_id)
        else:
            game = game[0]

        # Add information about current user to server data
        if not game.id in self.connected_users:
            self.connected_users[game.id] = [user]
        else:
            self.connected_users[game.id].append(user)

        # Wait for second player
        while len(self.connected_users[game.id]) < 2:
            print("Waiting for second player")
            await asyncio.sleep(0.5)

        # Assign websockets to the game
        player_1, player_2 = (
            self.connected_users[game.id][0],
            self.connected_users[game.id][1],
        )
        game.place_players(player_1, player_2)

        # Send initial board to clients
        await websocket.send(game.get_chessboard(websocket))

        # Collect full info about players and send to client
        user_info = user.copy()
        del user_info["websocket"]
        user_info["is_white"] = websocket == player_1["websocket"]
        if websocket == player_1["websocket"]:
            user_info["opponent_username"] = player_2["username"]
            user_info["opponent_elo_rating"] = player_2["elo_rating"]
        else:
            user_info["opponent_username"] = player_1["username"]
            user_info["opponent_elo_rating"] = player_1["elo_rating"]
        await websocket.send(json.dumps(user_info))

        return game

    async def main(self, websocket, game):
        async for message in websocket:
            if message == config.COMMAND_DRAW_OFFER:
                # send offer to both players
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
                for user in self.connected_users[game.id]:
                    if user["websocket"] != websocket:
                        await user["websocket"].send(config.MESSAGE_END_GAME)
                await websocket.send(config.MESSAGE_END_GAME)

            else:
                try:
                    start_field, end_field = (message).split(":")
                    game.handle_move(start_field, end_field, websocket)
                    if not game.is_over:
                        for user in self.connected_users[game.id]:
                            if user["websocket"] != websocket:
                                await user["websocket"].send(
                                    config.MESSAGE_CORRECT_MOVE
                                )
                                await user["websocket"].send(message)

                        await websocket.send(config.MESSAGE_CORRECT_MOVE)
                        await websocket.send(message)

                except Exception as error:
                    await websocket.send(
                        config.MESSAGE_INCORRECT_MOVE + "\n" + str(error)
                    )
                    continue

            if game.is_over:
                print("game over")
                for user in self.connected_users[game.id]:
                    if user["websocket"] != websocket:
                        await user["websocket"].send(config.MESSAGE_END_GAME)
                await websocket.send(config.MESSAGE_END_GAME)
                break

            # sending board
            for user in self.connected_users[game.id]:
                if user["websocket"] != websocket:
                    await user["websocket"].send(game.get_chessboard(user["websocket"]))
            await websocket.send(game.get_chessboard(websocket))


async def handler(websocket):
    game_id, username = await server.log_in_to_game(websocket)
    game = await server.create_game(websocket, game_id, username)
    await server.main(websocket, game)


async def start_server():
    print("Server started")
    async with websockets.serve(handler, "0.0.0.0", config.PORT, ping_interval=None):
        await asyncio.Future()


if __name__ == "__main__":
    server = ChessServer()
    asyncio.run(start_server())
