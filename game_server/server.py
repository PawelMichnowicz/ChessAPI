import asyncio
import json

import config
import websockets
from chess import Game
from graph import get_challanges_from_app_server


class ChessServer:
    def __init__(self) -> None:
        """Initialize the ChessServer object."""
        self.connected_users = {}

    def get_opponent_websocket(self, websocket, game):
        for user in self.connected_users[game.id]:
            if user["websocket"] != websocket:
                return user["websocket"]

    async def send_to_opponent(self, websocket, game, message):
        """Send a message to the opponent player's websocket.

        Args:
            websocket (WebSocketServerProtocol): Current player's websocket.
            game (Game): Instance of the game.
            message (str): Message to send to the opponent.
        """
        for user in self.connected_users[game.id]:
            if user["websocket"] != websocket:
                await user["websocket"].send(message)

    async def log_in_to_game(self, websocket):
        """Handle the initial authentication and login process for the user joining the
        game. Check if provided game id and username are correct.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection for the user.

        Returns:
            Tuple: A tuple containing the game ID and user information.
        """
        while True:
            try:
                # Receive game id from the client's WebSocket connection
                # and send query to app server by using it
                game_id = await websocket.recv()
                print(game_id)  # 1
                json_data = get_challanges_from_app_server(game_id)

                # Check if challange exists
                if not json_data["data"]["challange"]:
                    raise Exception("Game with this id doesn't exists")
                await websocket.send(config.MESSAGE_CORRECT_ID)

                # Check if received username matches with json data
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
        """Create a new game instance or assign the player to an existing game.

        This function creates a new game instance or assigns the player to an existing
        game based on the game ID.


        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection for the user.
            game_id (str): The ID of the game to join or create.
            user (dict): User data (username, elo_rating) and assigned websocket

        Returns:
            game (Game): The instance of the game.
        """

        # Create instance of the game
        game = Game.get(game_id)
        if not game:
            game = Game(game_id)
        else:
            game = game

        # Add information about current user to server data
        if game.id not in self.connected_users:
            self.connected_users[game.id] = [user]
            await websocket.send(json.dumps({"type": "waiting_for_opponent"}))
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

        user_info_json = json.dumps({"type": "game_info", "data": user_info})
        await websocket.send(user_info_json)

        # Send initial board to clients
        # await websocket.send(game.get_chessboard(websocket))

        return game

    async def main(self, websocket, game):
        """This function handles the main game loop for processing player moves and
        updating the game state accordingly.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection for the user.
            game(Game): The instance of the game.
        """

        # Loop to receive commands from the client's WebSocket connection
        # and send response message to them
        json_message = json.dumps(
            {
                "type": "game_state",
                "state": game.get_chessboard(websocket),
            }
        )
        await websocket.send(json_message)

        json_message_opponent = json.dumps(
            {
                "type": "game_state",
                "state": game.get_chessboard(
                    self.get_opponent_websocket(websocket, game)
                ),
            }
        )
        await self.send_to_opponent(
            websocket, game, json_message_opponent
        )

        async for message in websocket:
            print(message)
            data = json.loads(message)
            if data["type"] == "move":
                await websocket.send(json.dumps({"type": "move_confirmed"}))
                try:
                    start_field, end_field = data["from"], data["to"]
                    game.handle_move(start_field, end_field, websocket)

                    # If game is not over send message about last move and notify
                    # players about the correct move.
                    if not game.is_over:
                        # await self.send_to_opponent(
                        #     websocket, game, config.MESSAGE_CORRECT_MOVE
                        # )
                        # await self.send_to_opponent(websocket, game, message)
                        json_message = json.dumps(
                            {
                                "type": "game_state",
                                "state": game.get_chessboard(websocket),
                            }
                        )
                        await websocket.send(json_message)

                        json_message_opponent = json.dumps(
                            {
                                "type": "game_state",
                                "state": game.get_chessboard(
                                    self.get_opponent_websocket(websocket, game)
                                ),
                            }
                        )
                        await self.send_to_opponent(
                            websocket, game, json_message_opponent
                        )
                    # If game is over
                    else:
                        await self.send_to_opponent(
                            websocket, game, config.MESSAGE_END_GAME
                        )
                        await websocket.send(config.MESSAGE_END_GAME)

                # If provided move is inccorect send error to client and repeat loop
                except Exception as error:
                    # await websocket.send(
                    #     config.MESSAGE_INCORRECT_MOVE + "\n" + str(error)
                    # )
                    print(str(error))
                    continue

            # Sending board
            # print(game.get_chessboard(websocket))
            # for user in self.connected_users[game.id]:
            #     if user["websocket"] != websocket:
            #         opponent_chessboard = game.get_chessboard(user["websocket"])
            # await self.send_to_opponent(websocket, game, opponent_chessboard)
            # await websocket.send(game.get_chessboard(websocket))

            # If game is over send result description and winner username to players
            if game.is_over:
                game_result = {
                    "description": game.result_description,
                    "winner": None if not game.winner else game.winner.username,
                }
                await websocket.send(json.dumps(game_result))
                await self.send_to_opponent(websocket, game, json.dumps(game_result))
                return

    async def handler(self, websocket):
        """Function is responsible for handling the WebSocket connection for each
        client.

        It calls the `log_in_to_game` and `create_game` functions to authenticate user
        and set up the game environment. Then, it enters the `main` loop to handle
        messages and game actions until the game is over.

        Args:
            websocket (WebSocketServerProtocol): The client WebSocket connection object
        """
        # game_id, username = await self.log_in_to_game(websocket)
        message = await websocket.recv()
        data = json.loads(message)  # Załaduj wiadomość jako obiekt JSON
        print(data)
        game_id = data["gameId"]
        username = data["username"]

        user = {
            "username": username,
            "elo_rating": 0,
            "elo_rating_changes": 0,
            "websocket": websocket,
        }

        # Możesz teraz użyć game_id i username, np. do logowania lub bezpośrednio do stworzenia gry
        print(f"Otrzymano game_id: {game_id} i username: {username}")
        await websocket.send(json.dumps({"type": "login_success"}))

        game = await self.create_game(websocket, game_id, user)
        print("Stworzono gre")
        await self.main(websocket, game)

    async def start_server(self):
        """Start the WebSocket server.

        The server runs indefinitely and handles multiple connections simultaneously.
        """
        print("Server started")
        async with websockets.serve(
            self.handler, "0.0.0.0", config.PORT_WEBSOCKET, ping_interval=None
        ):
            await asyncio.Future()


if __name__ == "__main__":
    server = ChessServer()
    asyncio.run(server.start_server())
