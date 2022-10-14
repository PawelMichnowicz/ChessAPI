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
        print('Connected')

        while True:
            await ws.send(input("Provide id of your game: "))
            msg = await ws.recv()
            print(msg)
            if msg != 'id_ok':
                continue

            await ws.send(input("Provide your username: "))
            msg = await ws.recv()
            print(msg)
            if msg != 'username_ok':
                continue
            break

        end_game = False
        my_turn = str_to_bool(await ws.recv())
        while True:
            if my_turn:
                while my_turn:
                    await ws.send(input("Your Turn: "))
                    msg = await ws.recv()
                    if msg == 'ok':
                        board = await ws.recv()
                        print(board)
                        my_turn = False
                    elif msg == 'Check-mate':
                        board = await ws.recv()
                        print(board)
                        print(msg)
                        end_game = True
                        break
                    elif msg.startswith('Stalemate'):
                        board = await ws.recv()
                        print(board)
                        print(msg)
                        end_game = True
                        break
                    else: # incorrect move
                        print(msg)
                if end_game:
                    break
            else:
                print('Waiting for opp......') #
                msg = await ws.recv()
                if msg == 'end_game':
                    board = await ws.recv()
                    print(board)
                    break
                print(msg) # print opponent's move and chessboard
                my_turn = True

        print(await ws.recv()) # print result of game


asyncio.run(listen())


