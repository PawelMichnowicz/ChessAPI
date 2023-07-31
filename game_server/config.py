# network connection parameters
PORT_WEBSOCKET = 5050
QUERY_GET_CHALLANGE = 'query {{challange (gameId: "{}"){{id fromUser {{username eloRating}} toUser {{username eloRating}} eloRatingChanges }} }}'
MUTATION_END_GAME = (
    'mutation {{endGame(winnerUsername: "{}", challangeId:"{}"){{challange {{id}} }} }}'
)
URL_APP = "http://app:8000/graphql"
URL_WEBSOCKET = f"ws://localhost:{PORT_WEBSOCKET}"

# commands available to use by user during the game
COMMAND_DRAW_OFFER = "draw"
COMMAND_DRAW_DECLINED = "N"
COMMAND_DRAW_ACCEPTED = "Y"
COMMAND_GIVE_UP = "give up"

# messages used to communicate betwwen client and server
MESSAGE_CORRECT_ID = "id_ok"
MESSAGE_CORRECT_USERNAME = "username_ok"
MESSAGE_DRAW_OFFER = "draw offer"
MESSAGE_DRAW_DECLINED = "Declined"
MESSAGE_DRAW_ACCEPTED = "Accepted"
MESSAGE_END_GAME = "end game"
MESSAGE_INCORRECT_MOVE = "Try again:"
MESSAGE_CORRECT_MOVE = "move_ok"
