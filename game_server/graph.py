import json
import requests

import config


def send_result_to_app_server(winner_username, challange_id):
    """Send the game result to the application server.

    Args:
        winner_username (str): The username of the winner of the game.
        challange_id (str): The ID of the game challenge.

    Returns:
        dict: A dictionary containing the response data received from the server.
    """
    mutation = config.MUTATION_END_GAME.format(winner_username, challange_id)
    response = requests.post(url=config.URL_APP, json={"query": mutation})
    json_data = json.loads(response.text)
    return json_data


def get_challanges_from_app_server(game_id):
    """Get challenge data from the application server.

    Args:
        game_id (str): The ID of the game for which challenge data is requested.

    Returns:
        dict: A dictionary containing the response data received from the server.
    """
    query = config.QUERY_GET_CHALLANGE.format(game_id)
    response = requests.post(url=config.URL_APP, json={"query": query})
    json_data = json.loads(response.text)
    return json_data
