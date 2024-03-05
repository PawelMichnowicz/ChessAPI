import os
import platform
import asyncio
import json
import websockets

import config


class ChessClient:
    def __init__(self):
        """Initialize the ChessClient object."""
        self.url = config.URL_WEBSOCKET
        self.ws = None
        self.my_turn = False
        self.game_is_on = False
        self.user_data = {}
        self.game_info_description = ""
        self.last_move = ""

    async def connect(self):
        """Connect to the WebSocket server."""
        self.ws = await websockets.connect(self.url, ping_interval=None)

    @staticmethod
    def clear_terminal():
        """Clear the terminal screen based on the operating system used (Windows, macOS,
        or Linux)."""
        system = platform.system()
        if system == "Windows":
            os.system("cls")
        elif system == "Darwin" or system == "Linux":
            os.system("clear")

    async def authenticate_user(self):
        """Authenticate the user on the server."""
        while True:
            # Check if inputted id game exists
            await self.ws.send(input("Provide id of your game: "))
            msg = await self.ws.recv()
            print(msg)
            if msg != config.MESSAGE_CORRECT_ID:
                continue

            # Check if inputted username is assigned to the game
            await self.ws.send(input("Provide your username: "))
            msg = await self.ws.recv()
            print(msg)
            if msg != config.MESSAGE_CORRECT_USERNAME:
                continue
            break

    async def gather_game_info(self):
        """Gather information about the game."""
        self.user_data = json.loads(await self.ws.recv())
        self.user_data["elo_update_on_win"] = round(
            self.user_data["elo_rating_changes"]["win"] - self.user_data["elo_rating"],
            2,
        )
        self.user_data["elo_update_on_draw"] = round(
            self.user_data["elo_rating_changes"]["draw"] - self.user_data["elo_rating"],
            2,
        )
        self.user_data["elo_update_on_lose"] = round(
            self.user_data["elo_rating_changes"]["lose"] - self.user_data["elo_rating"],
            2,
        )
        self.game_info_description = (
            f"{self.user_data['username']}[{self.user_data['elo_rating']}] Vs. "
            f"{self.user_data['opponent_username']}"
            f"[{self.user_data['opponent_elo_rating']}] \n"
            "win:{self.user_data['elo_update_on_win']:+}pkt   "
            "draw:{self.user_data['elo_update_on_draw']:+}pkt   "
            "lose:{self.user_data['elo_update_on_lose']:+}pkt \n"
            f"[{config.COMMAND_DRAW_OFFER}]-offer a draw   "
            f"[{config.COMMAND_GIVE_UP}]-give up the game"
        )

    async def display_game_state(self, board):
        """Display the game state (board, player info, last move)

        Args:
            board ([str]): A string representing the chess board.
        """
        self.clear_terminal()
        print(self.game_info_description)
        print("")
        print(board)
        if self.last_move and self.my_turn:
            print(f"your last move:{self.last_move}")
        elif self.last_move and not self.my_turn:
            print(f"Opponent's last move: {self.last_move}")

    async def display_game_result(self, board):
        """Display the game result after it ends.

        Args:
            board ([str]): A string representing the chess board.
        """
        self.clear_terminal()
        print("The game is ended")
        print(board)
        print("")

        # print result description and points changes information
        game_result = json.loads(await self.ws.recv())
        print(game_result["description"])
        if self.user_data["username"] == game_result["winner"]:
            print(
                f"You gain {self.user_data['elo_update_on_win']} points through a win!"
            )
            print(
                f"Now your elo rating is equal "
                f"{self.user_data['elo_rating_changes']['win']}"
            )
        elif (
            self.user_data["username"] is None
            and self.user_data["elo_rating_changes"]["win"] > 0
        ):
            print(
                f"You gain {self.user_data['elo_update_on_draw']} "
                f"points through a draw!"
            )
            print(
                f"Now your elo rating is equal "
                f"{self.user_data['elo_rating_changes']['draw']}"
            )
        elif (
            self.user_data["username"] is None
            and self.user_data["elo_rating_changes"]["win"] < 0
        ):
            print(
                f"You lose {self.user_data['elo_update_on_draw']} "
                f"points through a draw!"
            )
            print(
                f"Now your elo rating is equal "
                f"{self.user_data['elo_rating_changes']['draw']}"
            )
        else:
            print(
                f"You lose {self.user_data['elo_update_on_lose']} "
                f"points through a lose!"
            )
            print(
                f"Now your elo rating is equal "
                f"{self.user_data['elo_rating_changes']['lose']}"
            )
        return

    async def listen(self):
        """Listen for messages from the server and handle the chess game interaction.

        It manages turn-taking, displaying game information and updating the game state
        accordingly. The client can offer a draw or resign the game. It receives and
        displays the game board, game info, and messages from the server.
        """
        await self.connect()
        print("Connected to the server!")

        await self.authenticate_user()
        await self.gather_game_info()
        board = await self.ws.recv()  # Get initial board before any move
        await self.display_game_state(board)

        self.game_is_on = True
        self.my_turn = self.user_data["is_white"]
        while self.game_is_on:
            if self.my_turn:
                await self.make_move()
            else:
                await self.wait_for_opponent()

            board = await self.ws.recv()
            await self.display_game_state(board)
            self.my_turn = not self.my_turn

        await self.display_game_result(board)
        await self.ws.close()

    async def make_move(self):
        """Handles the player's turn during the game. It sends the move or command to
        the server and processes the response to determine the next actions.

        Raises:
            Exception: If an unknown message is received from the server.
        """
        while True:
            await self.ws.send(input("Your Turn: "))
            msg = await self.ws.recv()

            # If the server informs about a draw offer handle the opponent's decision.
            if msg == config.MESSAGE_DRAW_OFFER:
                decision = await self.ws.recv()  # Wait for opponent decision
                if decision == config.MESSAGE_DRAW_DECLINED:
                    continue
                elif decision == config.MESSAGE_DRAW_ACCEPTED:
                    self.game_is_on = False
                    return

            elif msg == config.MESSAGE_CORRECT_MOVE:
                self.last_move = await self.ws.recv()
                break

            elif msg == config.MESSAGE_END_GAME:
                self.game_is_on = False
                return

            elif msg.startswith(config.MESSAGE_INCORRECT_MOVE):
                print(msg)
                continue

            else:
                print(msg)
                raise Exception("Unknown message")

    async def wait_for_opponent(self):
        """Wait for the opponent's move or command and processes the server's response
        to determine the next actions.

        Raises:
            Exception: If an unknown message is received from the server.
        """
        print("Waiting for opponent......")
        msg = await self.ws.recv()  # Wait for the server's response.

        # If the server informs about a draw offer, prompt the player to respond.
        if msg == config.MESSAGE_DRAW_OFFER:
            print("Draw offered:")
            while (
                True
            ):  # Keep repeating until an acceptable command or message is received.
                draw_response = input(
                    f"Type {config.COMMAND_DRAW_ACCEPTED}/"
                    f"{config.COMMAND_DRAW_DECLINED}: "
                )

                if draw_response.upper() == config.COMMAND_DRAW_ACCEPTED:
                    self.game_is_on = False
                    await self.ws.send(draw_response)
                    return
                elif draw_response.upper() == config.COMMAND_DRAW_DECLINED:
                    await self.ws.send(draw_response)
                    break
                else:
                    print("Invalid value")

        elif msg == config.MESSAGE_CORRECT_MOVE:
            self.last_move = await self.ws.recv()

        elif msg == config.MESSAGE_END_GAME:
            self.game_is_on = False

        else:
            print(msg)
            raise Exception("Unknown message")


if __name__ == "__main__":
    asyncio.run(ChessClient().listen())
