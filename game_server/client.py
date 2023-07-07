import websockets
import asyncio
import os
import platform

import config


from utils import str_to_bool


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

        my_turn = str_to_bool(await ws.recv())
        game_is_on = True
        await clear_terminal()
        print("The game started [game's data]")

        while game_is_on:
            if my_turn:
                while True:
                    await ws.send(input("Your Turn: "))
                    msg = await ws.recv()

                    if msg == config.COMMAND_DRAW_OFFER:
                        decision = await ws.recv()
                        if decision == config.MESSAGE_DRAW_DECLINED:
                            continue
                        elif decision == config.MESSAGE_DRAW_ACCEPTED:
                            break

                    elif msg == config.MESSAGE_CORRECT_MOVE:
                        break

                    elif msg.startswith(config.MESSAGE_INCORRECT_MOVE):
                        print(msg)
                        continue

                    else:
                        print(msg)
                        raise Exception("Unknown command")

                await clear_terminal()
                board = await ws.recv()
                print("@@@@ board @@@@")
                print(board)

                if (
                    msg == config.MESSAGE_DRAW_OFFER and decision == config.MESSAGE_DRAW_ACCEPTED
                ) or msg == config.MESSAGE_END_GAME:  # change
                    game_is_on = False
                    break
                else:  # correct move
                    my_turn = False

            else:
                print("Waiting for opponent......")
                msg = await ws.recv()

                if msg == config.MESSAGE_DRAW_OFFER:
                    print("Draw offered:")
                    while True:
                        draw_response = input(f"Type {config.COMMAND_DRAW_ACCEPTED}/{config.COMMAND_DRAW_DECLINED}: ")
                        if (
                            draw_response.upper() == config.COMMAND_DRAW_ACCEPTED or draw_response.upper() == config.COMMAND_DRAW_DECLINED
                        ):
                            await ws.send(draw_response)
                            break
                        else:
                            print("Invalid value")
                    continue

                board = await ws.recv()
                await clear_terminal()
                print("|||| board |||||")
                print(board)
                if (
                    "draw_response" in locals() and draw_response == config.COMMAND_DRAW_ACCEPTED
                ):  # end of the game
                    break
                else:  # correct move
                    my_turn = True

asyncio.run(listen())
