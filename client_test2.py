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

    async def send_mess():
        while True:
            await ws.send(input("Your Turn: "))
            msg = await ws.recv()
            print(msg)

    async def recv_mess():
        print('Waiting for opp......')
        msg = await ws.recv()
        print(f"Opponent made: {msg}")



    async with websockets.connect(url, ping_interval=None) as ws:

        task_1 = asyncio.create_task(send_mess())
        task_2 = asyncio.create_task(recv_mess())
        while True:
            await asyncio.wait(
                [task_1, task_2],
                return_when=asyncio.FIRST_COMPLETED
            )



asyncio.run(listen())




