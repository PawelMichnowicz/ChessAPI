import json
from unittest.mock import AsyncMock, patch

import config
import pytest
from client import ChessClient


@pytest.mark.asyncio
def prepare_chess_client_environment(test_messages, *args):
    """Helper function to prepare tests for the make_move and waiting_for_opponent
    method.

    It mocks the WebSocket connection and sets up predefined responses to simulate
    server behavior.
    """
    client = ChessClient()
    client.game_is_on = True
    client.ws = AsyncMock()

    # Simulate server responses based on the test_messages list
    client.ws.recv = AsyncMock(side_effect=test_messages)
    client.ws.send = AsyncMock()

    return client


@pytest.mark.asyncio
@patch("builtins.input", return_value="")
async def test_make_move_correct_move(*args):
    """Tests make_move handling a correct move scenario where the server confirms the
    move."""
    test_messages = [config.MESSAGE_CORRECT_MOVE, "e2:e4"]
    client = prepare_chess_client_environment(test_messages)
    await client.make_move()

    # Verify the last move was correctly set and only one move was sent
    assert client.last_move == "e2:e4"
    assert client.ws.send.call_count == 1


@pytest.mark.asyncio
@patch("builtins.input", return_value="")
async def test_make_move_declined_draw_offer_and_correct_move(*args):
    """Tests make_move handling a scenario where a draw offer is declined and after that
    is correct move."""
    test_messages = [
        config.MESSAGE_DRAW_OFFER,
        config.MESSAGE_DRAW_DECLINED,
        config.MESSAGE_CORRECT_MOVE,
        "e2:e4",
    ]
    client = prepare_chess_client_environment(test_messages)
    await client.make_move()

    # Verify that two messages were sent and the game wasn't ended
    assert client.ws.send.call_count == 2
    assert client.game_is_on


@pytest.mark.asyncio
@patch("builtins.input", return_value="")
async def test_make_move_draw_offer_accepted(*args):
    """Tests make_move handling a scenario where a draw offer is accepted, ending the
    game."""
    test_messages = [config.MESSAGE_DRAW_OFFER, config.MESSAGE_DRAW_ACCEPTED]
    client = prepare_chess_client_environment(test_messages)
    await client.make_move()

    # Verify that a draw acceptance was sent and the game ended
    assert client.ws.send.call_count == 1
    assert client.game_is_on is False


@pytest.mark.asyncio
async def test_wait_for_opponent_correct_move():
    """Tests wait_for_opponent handling a correct move from the opponent and then ending
    the game."""
    test_messages = [config.MESSAGE_CORRECT_MOVE, "e2:e4", config.MESSAGE_END_GAME]
    client = prepare_chess_client_environment(test_messages)
    await client.wait_for_opponent()
    await client.wait_for_opponent()

    # Verify the last move was correctly set and the game ended
    assert client.last_move == "e2:e4"
    assert client.game_is_on is False


@pytest.mark.asyncio
@patch("builtins.input", return_value=config.COMMAND_DRAW_DECLINED)
async def test_wait_for_opponent_draw_offer_declined(*args):
    """Tests wait_for_opponent handling a scenario where a draw offer is declined."""
    test_messages = [config.MESSAGE_DRAW_OFFER, "unwanted_message"]
    client = prepare_chess_client_environment(test_messages)
    await client.wait_for_opponent()

    # Verify that a draw decline was sent and the game continued
    assert client.game_is_on
    assert client.ws.send.call_count == 1
    client.ws.send.assert_called_with(config.COMMAND_DRAW_DECLINED)


@pytest.mark.asyncio
@patch("builtins.input", return_value=config.COMMAND_DRAW_ACCEPTED)
async def test_wait_for_opponent_draw_offer_accepted(*args):
    """Tests wait_for_opponent handling a scenario where a draw offer is accepted,
    ending the game."""
    test_messages = [config.MESSAGE_DRAW_OFFER, config.MESSAGE_END_GAME]
    client = prepare_chess_client_environment(test_messages)
    await client.wait_for_opponent()

    # Verify that a draw acceptance was sent and the game ended
    assert client.game_is_on is False
    assert client.ws.send.call_count == 1
    client.ws.send.assert_called_with(config.COMMAND_DRAW_ACCEPTED)


@pytest.mark.asyncio
@patch("websockets.connect", new_callable=AsyncMock)
async def test_connect(mock_connect):
    """Tests the client's ability to connect to the WebSocket server."""
    client = ChessClient()
    await client.connect()
    mock_connect.assert_called_with(client.url, ping_interval=None)
    assert client.ws is not None


@pytest.mark.asyncio
@patch(
    "builtins.input",
    side_effect=["invalid_id", "valid_id", "username", "unwanted_input"],
)
async def test_authenticate_user(mock_input):
    """Tests the authenticate_user method to handle user authentication with retries for
    invalid inputs."""
    # Create an instance of the client
    client = ChessClient()

    # Mock the behavior for client websocket
    client.ws = AsyncMock()
    client.ws.send = AsyncMock()
    client.ws.recv = AsyncMock(
        side_effect=[
            "error",
            config.MESSAGE_CORRECT_ID,
            config.MESSAGE_CORRECT_USERNAME,
            "unwanted_recv_message",
        ]
    )

    await client.authenticate_user()

    # Verify that the send and recv methods were called with the expected arguments
    client.ws.send.assert_any_call("invalid_id")
    client.ws.send.assert_any_call("valid_id")
    client.ws.send.assert_any_call("username")
    assert client.ws.send.call_count == 3


@pytest.mark.asyncio
async def test_gather_game_info():
    """Tests gathering game information from the server and updating the client state
    accordingly."""
    # Create an instance of the client
    client = ChessClient()

    # Simulate server response with game information
    game_info_response = json.dumps(
        {
            "username": "test_user",
            "elo_rating_changes": {"win": 1050, "draw": 1000, "lose": 950},
            "elo_rating": 1000,
            "opponent_username": "opponent_user",
            "opponent_elo_rating": 950,
        }
    )

    # Mock the behavior for client websocket
    client.ws = AsyncMock()
    client.ws.recv = AsyncMock(return_value=game_info_response)

    await client.gather_game_info()

    # Verify that game information has been properly updated
    assert client.user_data["username"] == "test_user"
    assert client.user_data["elo_rating"] == 1000
    assert client.user_data["opponent_username"] == "opponent_user"
    # Also verify calculations based on received data
    assert client.user_data["elo_update_on_win"] == 50
    assert client.user_data["elo_update_on_draw"] == 0
    assert client.user_data["elo_update_on_lose"] == -50
