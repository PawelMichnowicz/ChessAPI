import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import config
import pytest
from server import ChessServer


@pytest.mark.asyncio
def setup_main_test_environment(test_messages):
    """
    Helper function to set up the testing environment.
    It creates mocked instances needed for testing the server's main function.
    """
    # Mock WebSocket to simulate receiving client messages from test_commands list.
    mocked_websocket = MagicMock()
    mocked_websocket.__aiter__.return_value = iter(test_messages)
    mocked_websocket.send = AsyncMock()
    opponent_websocket = AsyncMock()

    # Mock the game object with initial states and methods.
    game = Mock()
    game.is_over = False
    game.id = "game_id"
    game.handle_move = Mock()
    game.end_with_draw = Mock()
    game.end_with_win = Mock()
    game.get_chessboard.return_value = ""

    # Setup the ChessServer instance with mocked players connected.
    server = ChessServer()
    server.connected_users[game.id] = [
        {"username": "player_1", "elo_rating": "100", "websocket": mocked_websocket},
        {"username": "player_2", "elo_rating": "100", "websocket": opponent_websocket},
    ]
    server.send_to_opponent = AsyncMock()

    return game, mocked_websocket, server


@pytest.mark.asyncio
async def test_main_with_correct_moves():
    """
    Test the main function behavior when few correct moves.
    """
    test_messages = [
        '{"type":"move","from":"d2","to":"d3"}',
        '{"type":"move","from":"d3","to":"d4"}',
        '{"type":"move","from":"b2","to":"a1"}',
    ]
    game, websocket, server = setup_main_test_environment(test_messages)
    await server.main(websocket, game)

    # Check if each move was processed and acknowledged.
    game.handle_move.assert_any_call("d2", "d3", websocket)
    game.handle_move.assert_any_call("d3", "d4", websocket)
    game.handle_move.assert_called_with("b2", "a1", websocket)

    # Verify whether after each move the game state has been sent to both players.
    websocket.send.call_count == 3
    server.send_to_opponent.call_count == 3


@pytest.mark.asyncio
async def test_main_with_draw_accepted():
    pass


@pytest.mark.asyncio
async def test_main_with_draw_declined_and_resigned():
    pass


@pytest.mark.asyncio
async def test_main_with_ending_move():
    """
    Test the main function with a move leading to game ending.
    """

    # Mock the behavior for an ending move.
    def handle_ending_move(*args, **kwargs):
        game.is_over = True
        game.winner = Mock()
        game.winner.username = "player_1"
        game.result_description = ""

    test_messages = [
        '{"type":"move","from":"e2","to":"e4"}',
    ]
    game, websocket, server = setup_main_test_environment(test_messages)
    game.handle_move = Mock(side_effect=handle_ending_move)
    await server.main(websocket, game)

    # Assert that the ending move is processed correctly and the game ends.
    game.handle_move.assert_called_once_with("e2", "e4", websocket)
    server.send_to_opponent.assert_any_call(websocket, game, config.MESSAGE_END_GAME)
    websocket.send.assert_any_call(config.MESSAGE_END_GAME)


@pytest.mark.asyncio
async def test_main_with_incorrect_move():
    pass


@pytest.mark.asyncio
async def test_create_game():
    """
    Test the game creation process to ensure that two players can join the same game
    and that their information is correctly registered and acknowledged by the server.
    """
    game_id = "test_game_id"
    websocket_player1 = AsyncMock()
    websocket_player2 = AsyncMock()
    player_1 = {
        "username": "player_1",
        "elo_rating": "1500",
        "websocket": websocket_player1,
    }
    player_2 = {
        "username": "player_2",
        "elo_rating": "1600",
        "websocket": websocket_player2,
    }

    # Instantiate the game server and create game sessions for both players.
    server = ChessServer()
    game_creation_tasks = [
        server.create_game(websocket_player1, game_id, player_1),
        server.create_game(websocket_player2, game_id, player_2),
    ]
    games = await asyncio.gather(*game_creation_tasks)

    # Verify both players join the same game instance
    # and the game ID is registered in connected users.
    assert games[0] is games[1]
    assert game_id in server.connected_users

    # Check if the players' information is correctly recorded in the game session.
    player_1_info, player_2_info = server.connected_users[game_id]
    assert player_1_info["username"] == player_1["username"]
    assert player_2_info["username"] == player_2["username"]

    # Confirm the message sent to player 1 contains correct opponent's username
    call_with_game_info = websocket_player1.send.call_args_list[2][0]
    sent_data = json.loads(call_with_game_info[0])
    assert sent_data["data"]["opponent_username"] == player_2["username"]


@pytest.mark.asyncio
async def test_log_in_to_game_successful():
    """
    Test the login process to ensure a player can successfully log in to the game
    with a valid game ID and username, and verify the server responds with correct
    messages.
    """
    # Mock WebSocket to simulate player's login attempts.
    websocket_mock = AsyncMock()
    websocket_mock.recv = AsyncMock(side_effect=["valid_game_id", "valid_username"])
    expected_json_data = {
        "data": {
            "challange": {
                "fromUser": {"username": "valid_username", "eloRating": "1200"},
                "toUser": {"username": "other_user", "eloRating": "1100"},
                "eloRatingChanges": json.dumps(
                    {"valid_username": "+10", "other_user": "-10"}
                ),
            }
        }
    }

    # Patch the server's method to respond with the expected login data.
    with patch(
        "server.get_challanges_from_app_server", return_value=expected_json_data
    ):
        server = ChessServer()
        game_id, user = await server.log_in_to_game(websocket_mock)

        # Verify login was successful with expected game ID and user info.
        assert game_id == "valid_game_id"
        assert user["username"] == "valid_username"
        assert user["elo_rating"] == "1200"
        assert user["elo_rating_changes"] == "+10"

        # Check if correct messages were sent during the login process.
        expected_calls = [
            call(config.MESSAGE_CORRECT_ID),
            call(config.MESSAGE_CORRECT_USERNAME),
        ]
        websocket_mock.send.assert_has_calls(expected_calls, any_order=True)


@pytest.mark.asyncio
async def test_handler():
    pass
