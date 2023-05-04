import websockets
import asyncio

from utils import str_to_bool


async def listen():
    url = "ws://localhost:5050"

    async with websockets.connect(url, ping_interval=None) as ws:
        print("Connected")

        while True:
            await ws.send(input("Provide id of your game: "))
            msg = await ws.recv()
            print(msg)
            if msg != "id_ok":
                continue

            await ws.send(input("Provide your username: "))
            msg = await ws.recv()
            print(msg)
            if msg != "username_ok":
                continue
            break

        my_turn = str_to_bool(await ws.recv())
        game_is_on = True
        while game_is_on:
            if my_turn:
                while True:
                    await ws.send(input("Your Turn: "))
                    msg = await ws.recv()

                    # if player made illegal move, repeat attempt
                    if msg.startswith("Try again"):
                        print(msg)
                        continue

                    board = await ws.recv()
                    print(board)
                    if msg:  # end of the game
                        game_is_on = False
                        break
                    else:  # correct move
                        my_turn = False
                        break
            else:
                print("Waiting for opponent......")  #
                msg = await ws.recv()
                board = await ws.recv()
                print(board)
                if msg:  # end of the game
                    break
                else:  # correct move
                    my_turn = True

        print(msg)


asyncio.run(listen())
