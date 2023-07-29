import os
import platform
import asyncio
import json
import websockets

import config


class ChessClient:
    def __init__(self):
        self.url = "ws://localhost:5050"
        self.ws = None
        self.my_turn = False
        self.game_is_on = False
        self.user_data = {}
        self.game_info = ""
        self.last_move = ""

    async def connect(self):
        self.ws = await websockets.connect(self.url, ping_interval=None)

    @staticmethod
    def clear_terminal():
        system = platform.system()
        if system == "Windows":
            os.system("cls")
        elif system == "Darwin" or system == "Linux":
            os.system("clear")

    async def authenticate_user(self):
        while True:
            await self.ws.send(input("Provide id of your game: "))
            msg = await self.ws.recv()
            print(msg)
            if msg != config.MESSAGE_CORRECT_ID:
                continue

            await self.ws.send(input("Provide your username: "))
            msg = await self.ws.recv()
            print(msg)
            if msg != config.MESSAGE_CORRECT_USERNAME:
                continue
            break

    async def gather_game_info(self):
        self.user_data = json.loads(await self.ws.recv())
        self.user_data['elo_update_on_win'] = round(
            self.user_data["elo_rating_changes"]["win"] - self.user_data["elo_rating"],
            2,
        )
        self.user_data['elo_update_on_draw'] = round(
            self.user_data["elo_rating_changes"]["draw"] - self.user_data["elo_rating"],
            2,
        )
        self.user_data['elo_update_on_lose'] = round(
            self.user_data["elo_rating_changes"]["lose"] - self.user_data["elo_rating"],
            2,
        )
        self.game_info = (
            f"{self.user_data['username']}[{self.user_data['elo_rating']}] Vs. {self.user_data['opponent_username']}[{self.user_data['opponent_elo_rating']}] \n"
            f"win:{self.user_data['elo_update_on_win']:+}pkt   draw:{self.user_data['elo_update_on_draw']:+}pkt   lose:{self.user_data['elo_update_on_lose']:+}pkt \n"
            f"[{config.COMMAND_DRAW_OFFER}]-offer a draw   [{config.COMMAND_GIVE_UP}]-give up the game"
        )

    async def display_game_state(self, board):
        self.clear_terminal()
        print(self.game_info)
        print("")
        print(board)
        if self.last_move and self.my_turn:
            print(f"your last move:{self.last_move}")
        elif self.last_move and not self.my_turn:
            print(f"Opponent's last move: {self.last_move}")

    async def display_game_result(self):
        print("The game is ended")

        game_result = json.loads(await self.ws.recv())
        print(game_result["description"])
        if self.user_data["username"] == game_result["winner"]:
            print(f"You gain {self.user_data['elo_update_on_win']} points through a win!")
            print(f"Now your elo rating is equal {self.user_data['elo_rating_changes']['win']}")
        elif self.user_data["username"] is None and self.user_data['elo_rating_changes']['win']>0:
            print(f"You gain {self.user_data['elo_update_on_draw']} points through a draw!")
            print(f"Now your elo rating is equal {self.user_data['elo_rating_changes']['draw']}")
        elif self.user_data["username"] is None and self.user_data['elo_rating_changes']['win']<0:
            print(f"You lose {self.user_data['elo_update_on_draw']} points through a draw!")
            print(f"Now your elo rating is equal {self.user_data['elo_rating_changes']['draw']}")
        else:
            print(f"You lose {self.user_data['elo_update_on_lose']} points through a lose!")
            print(f"Now your elo rating is equal {self.user_data['elo_rating_changes']['lose']}")
        return

    async def listen(self):
        await self.connect()
        print("Connected to the server!")

        await self.authenticate_user()
        await self.gather_game_info()

        initial_board = await self.ws.recv()
        await self.display_game_state(initial_board)

        self.game_is_on = True
        self.my_turn = self.user_data["is_white"]
        while self.game_is_on:
            if self.my_turn:
                await self.make_move()
            else:
                await self.wait_for_opponent()


            board = await self.ws.recv()
            print(f'test board {board}')
            await self.display_game_state(board)
            self.my_turn = not self.my_turn

        await self.display_game_result()
        await self.ws.close()

    async def make_move(self):
        while True:
            await self.ws.send(input("Your Turn: "))
            msg = await self.ws.recv()

            if msg == config.MESSAGE_DRAW_OFFER:
                decision = await self.ws.recv()
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
        print("Waiting for opponent......")
        msg = await self.ws.recv()

        if msg == config.MESSAGE_DRAW_OFFER:
            print("Draw offered:")
            while True:
                draw_response = input(
                    f"Type {config.COMMAND_DRAW_ACCEPTED}/{config.COMMAND_DRAW_DECLINED}: "
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
            return

        elif msg == config.MESSAGE_CORRECT_MOVE:
            self.last_move = await self.ws.recv()

        elif msg == config.MESSAGE_END_GAME:
            self.game_is_on = False
            return
        else:
            print(msg)
            raise Exception("Unknown message")


if __name__ == "__main__":
    asyncio.run(ChessClient().listen())
