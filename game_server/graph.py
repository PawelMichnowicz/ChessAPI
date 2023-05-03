import json
import requests

query = """
    query {
        allChallanges {
            id
        }
    }"""

query = 'query {{challange (gameId: "{}"){{id fromUser {{username}} toUser {{username}} }} }}'
query = query.format("47c9e51a-47b2-41de-aedf-535b7e7fb5d3")


def send_result(winner_username, challange_id):
    URL = "http://app:8000/graphql"
    mutation = 'mutation {{endGame(winnerUsername: "{}", challangeId:"{}"){{challange {{id}} }} }}'
    mutation = mutation.format(winner_username, challange_id)
    response = requests.post(url=URL, json={"query": mutation})
    json_data = json.loads(response.text)
    return json_data
