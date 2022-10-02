import json
import requests
query = """
    query {
        allChallanges {
            id
        }
    }"""

query = 'query {{challange (gameId: "{}"){{id fromPlayer {{username}} toPlayer {{username}} }} }}'
query = query.format("47c9e51a-47b2-41de-aedf-535b7e7fb5d3")

url = 'http://app:8000/graphql'

r = requests.post(url, json={'query': query})
print(r.status_code)
json_data = json.loads(r.text)
print(json_data['data']['challange'])

if json_data['data']['challange']['fromPlayer']['username'] != 'miska' and json_data['data']['challange']['toPlayer']['username'] != 'miska':
    print('ok')
