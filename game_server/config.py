# network connection parameters
PORT = 5050
QUERY_GET_CHALLANGE = 'query {{challange (gameId: "{}"){{id fromUser {{username eloRating}} toUser {{username eloRating}} eloRatingChanges }} }}'
URL = "http://app:8000/graphql"
URL_WEBSOCKET = "ws://localhost:5050"

# commands available to use by user
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
