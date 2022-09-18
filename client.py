import websockets
import asyncio

def str_to_bool(str):
    if str == 'True':
         return True
    elif str == 'False':
         return False
    else:
         raise Exception(str)

# ogarnia wszystko co przychodzi z serwera




async def listen():

    url = "ws://localhost:5050"

    async with websockets.connect(url, ping_interval=None) as ws:

        my_turn = not str_to_bool(await ws.recv())

        while True:

            if my_turn:
                while True:
                    await ws.send(input("Your Turn: "))
                    msg = await ws.recv()
                    print(msg)
                    if msg=='ok':
                        break
            else:
                print('Waiting for opp......')
                msg = await ws.recv()
                print(f"Opponent made: {msg}")
            my_turn = not my_turn


asyncio.run(listen())