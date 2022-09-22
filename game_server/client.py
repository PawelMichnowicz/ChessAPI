import websockets
import asyncio


def str_to_bool(value):
    if value == 'True':
        return True
    elif value == 'False':
        return False
    else:
        raise Exception(value)


async def listen():

    url = "ws://localhost:5050"

    async with websockets.connect(url, ping_interval=None) as ws:

        my_turn = str_to_bool(await ws.recv())
        while True:

            if my_turn:
                # while True:
                while my_turn:
                    await ws.send(input("Your Turn: "))
                    msg = await ws.recv()
                    if msg == 'ok':
                        board = await ws.recv()
                        print(board)
                        my_turn = False
            else:
                print('Waiting for opp......')
                print(await ws.recv())
                my_turn = True


asyncio.run(listen())
