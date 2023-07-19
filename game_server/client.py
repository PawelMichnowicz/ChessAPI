import asyncio
import json
import os
import platform
import websockets

import config


async def clear_terminal():
    system = platform.system()
    if system == "Windows":
        os.system("cls")
    elif system == "Darwin" or system == "Linux":
        os.system("clear")


async def listen():
    url = "ws://localhost:5050"

    async with websockets.connect(url, ping_interval=None) as ws:
        print("Connected to the server!")

        while True:
            await ws.send(input("Provide id of your game: "))
            msg = await ws.recv()
            print(msg)
            if msg != config.MESSAGE_CORRECT_ID:
                continue

            await ws.send(input("Provide your username: "))
            msg = await ws.recv()
            print(msg)
            if msg != config.MESSAGE_CORRECT_USERNAME:
                continue
            break

        # Declare displayed data about game
        initial_board = await ws.recv()
        user_data = json.loads(await ws.recv())
        elo_update_on_win = round(
            user_data["elo_rating_changes"]["win"] - user_data["elo_rating"], 2
        )
        elo_update_on_draw = round(
            user_data["elo_rating_changes"]["draw"] - user_data["elo_rating"], 2
        )
        elo_update_on_lose = round(
            user_data["elo_rating_changes"]["lose"] - user_data["elo_rating"], 2
        )
        game_info = (
            f"{user_data['username']}[{user_data['elo_rating']}] Vs. {user_data['opponent_username']}[{user_data['opponent_elo_rating']}] \n"
            f"win:{elo_update_on_win:+}pkt   draw:{elo_update_on_draw:+}pkt   lose:{elo_update_on_lose:+}pkt \n"
            f"[{config.COMMAND_DRAW_OFFER}]-offer a draw   [{config.COMMAND_GIVE_UP}]-give up the game"
        )

        game_is_on = True
        await clear_terminal()
        print("The game started")
        print(game_info)
        print("")
        print(initial_board)

        my_turn = user_data["is_white"]
        while game_is_on:
            if my_turn:
                while True:
                    await ws.send(input("Your Turn: "))
                    msg = await ws.recv()

                    if msg == config.MESSAGE_DRAW_OFFER:
                        decision = await ws.recv()
                        if decision == config.MESSAGE_DRAW_DECLINED:
                            continue
                        elif decision == config.MESSAGE_DRAW_ACCEPTED:
                            break

                    elif msg == config.MESSAGE_CORRECT_MOVE:
                        last_move = await ws.recv()
                        break

                    elif msg == config.MESSAGE_END_GAME:
                        break

                    elif msg.startswith(config.MESSAGE_INCORRECT_MOVE):
                        print(msg)
                        continue

                    else:
                        print(msg)
                        raise Exception("Unknown messsage")

                if (
                    msg == config.MESSAGE_DRAW_OFFER
                    and decision == config.MESSAGE_DRAW_ACCEPTED
                ) or msg == config.MESSAGE_END_GAME:
                    game_is_on = False
                    break
                else:  # correct move
                    my_turn = False

                await clear_terminal()
                board = await ws.recv()
                print(game_info)
                print("")
                print(board)
                if "last_move" in locals():
                    print(f"your last move:{last_move}")

            else:
                print("Waiting for opponent......")
                msg = await ws.recv()

                if msg == config.MESSAGE_DRAW_OFFER:
                    print("Draw offered:")
                    while True:
                        draw_response = input(
                            f"Type {config.COMMAND_DRAW_ACCEPTED}/{config.COMMAND_DRAW_DECLINED}: "
                        )
                        if (
                            draw_response.upper() == config.COMMAND_DRAW_ACCEPTED
                            or draw_response.upper() == config.COMMAND_DRAW_DECLINED
                        ):
                            await ws.send(draw_response)
                            break
                        else:
                            print("Invalid value")
                    continue

                elif msg == config.MESSAGE_CORRECT_MOVE:
                    last_move = await ws.recv()

                # Check if there is an accepted draw or end of the game
                if (
                    "draw_response" in locals()
                    and draw_response == config.COMMAND_DRAW_ACCEPTED
                ) or msg == config.MESSAGE_END_GAME:
                    break
                else:
                    my_turn = True

                board = await ws.recv()
                await clear_terminal()
                print(game_info)
                print("")
                print(board)
                if "last_move" in locals():
                    print(f"Opponent's last move: {last_move}")


asyncio.run(listen())
