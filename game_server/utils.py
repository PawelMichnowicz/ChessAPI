

async def send_response_to_player(websocket, game):
    await websocket.send(game.result_description)
    await websocket.send(game.get_chessboard(websocket))





async def send_response_to_opponent(connected_users, websocket, game):
    for user in connected_users[game.id]:
        if user["websocket"] != websocket:
            await user["websocket"].send(game.result_description)
            await user["websocket"].send(game.get_chessboard(websocket))


def str_to_bool(value):
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        raise Exception(value)
