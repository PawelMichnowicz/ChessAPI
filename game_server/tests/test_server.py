import asyncio
import pytest
from unittest.mock import patch, call, AsyncMock, Mock, MagicMock
import json

import config
from server import ChessServer


@pytest.mark.asyncio
def setup_main_test_environment(test_commands):
    """
    Helper function to set up the testing environment.
    It creates mocked instances needed for testing the server's main function.
    """
    # Mock WebSocket to simulate receiving client messages from test_commands list.
    mocked_websocket = MagicMock()
    mocked_websocket.__aiter__.return_value = iter(test_commands)
    mocked_websocket.send = AsyncMock()
    opponent_websocket = AsyncMock()

    # Mock the game object with initial states and methods.
    game = Mock()
    game.is_over = False
    game.id = "game_id"
    game.handle_move = Mock()
    game.end_with_draw = Mock()
    game.end_with_win = Mock()
    game.get_chessboard = Mock()

    # Setup the ChessServer instance with mocked players connected.
    server = ChessServer()
    server.connected_users[game.id] = [
        {"username": "player_1", "elo_rating": "100", "websocket": mocked_websocket},
        {"username": "player_2", "elo_rating": "100", "websocket": opponent_websocket},
    ]
    server.send_to_opponent = AsyncMock()

    return game, mocked_websocket, server


@pytest.mark.asyncio
async def test_main_with_draw_accepted():
    """
    Test the main function behavior when a draw is offered and accepted.
    """
    test_commands = [config.COMMAND_DRAW_OFFER, config.COMMAND_DRAW_ACCEPTED]
    game, websocket, server = setup_main_test_environment(test_commands)
    await server.main(websocket, game)

    # Assert that the correct messages are sent for a draw offer and acceptance.
    websocket.send.assert_any_call(config.MESSAGE_DRAW_OFFER)
    server.send_to_opponent.assert_any_call(websocket, game, config.MESSAGE_DRAW_OFFER)
    server.send_to_opponent.assert_any_call(
        websocket, game, config.MESSAGE_DRAW_ACCEPTED
    )
    game.end_with_draw.assert_called_once()


@pytest.mark.asyncio
async def test_main_with_draw_declined_and_resigned():
    """
    Test the main function behavior when a offered draw is declined and the game is resigned.
    """
    test_commands = [
        config.COMMAND_DRAW_OFFER,
        config.COMMAND_DRAW_DECLINED,
        config.COMMAND_GIVE_UP,
    ]
    game, websocket, server = setup_main_test_environment(test_commands)
    await server.main(websocket, game)

    # Assert that the game ends without a draw and a resignation is processed.
    game.end_with_draw.assert_not_called()
    game.end_with_win.assert_called_once()
    server.send_to_opponent.assert_any_call(websocket, game, config.MESSAGE_END_GAME)


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

    test_commands = ["e2:e4"]
    game, websocket, server = setup_main_test_environment(test_commands)
    game.handle_move = Mock(side_effect=handle_ending_move)
    await server.main(websocket, game)

    # Assert that the ending move is processed correctly and the game ends.
    game.handle_move.assert_called_once_with("e2", "e4", websocket)
    server.send_to_opponent.assert_any_call(websocket, game, config.MESSAGE_END_GAME)
    websocket.send.assert_any_call(config.MESSAGE_END_GAME)


@pytest.mark.asyncio
async def test_main_with_incorrect_move():
    """
    Test for handling incorrect move.
    """

    # Mock the behavior for an incorrect move.
    def handle_ending_move(*args, **kwargs):
        raise ValueError(config.EMPTY_START_FIELD)

    test_commands = ["e2:e4"]
    game, websocket, server = setup_main_test_environment(test_commands)
    game.handle_move = Mock(side_effect=handle_ending_move)
    await server.main(websocket, game)

    # Assert that an incorrect move results in the appropriate error message being sent.
    game.handle_move.assert_called_once_with("e2", "e4", websocket)
    websocket.send.assert_any_call(
        config.MESSAGE_INCORRECT_MOVE + "\n" + config.EMPTY_START_FIELD
    )


@pytest.mark.asyncio
async def test_main_with_casual_moves():
    """
    Test handling a sequence of valid chess moves .
    """
    test_commands = ["a3:a4", "c2:a2", "c4:d5"]
    game, websocket, server = setup_main_test_environment(test_commands)
    await server.main(websocket, game)

    # Check if each move was processed and acknowledged.
    game.handle_move.assert_has_calls(
        [
            call("a3", "a4", websocket),
            call("c2", "a2", websocket),
            call("c4", "d5", websocket),
        ]
    )
    # Verify that each command was sent to both the player and the opponent.
    for command in test_commands:
        websocket.send.assert_any_call(command)
        server.send_to_opponent.assert_any_call(websocket, game, command)


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

    # Verify both players join the same game instance and the game ID is registered in connected users.
    assert games[0] is games[1]
    assert game_id in server.connected_users

    # Check if the players' information is correctly recorded in the game session.
    player_1_info, player_2_info = server.connected_users[game_id]
    assert player_1_info["username"] == player_1["username"]
    assert player_2_info["username"] == player_2["username"]

    # Confirm the initial message sent to player 1 contains correct opponent's username.
    first_call_player1 = websocket_player1.send.call_args_list[0][0]
    sent_data = json.loads(first_call_player1[0])
    assert sent_data["opponent_username"] == player_2["username"]


@pytest.mark.asyncio
async def test_log_in_to_game_successful():
    """
    Test the login process to ensure a player can successfully log in to the game
    with a valid game ID and username, and verify the server responds with correct messages.
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
    """
    Test the `handler` function to ensure it properly orchestrates the game session setup,
    including player login, game creation, and entering the main game loop.
    """
    server = ChessServer()

    game_id = "game123"
    user = "player1"

    # Patch server methods to simulate specific behaviors and outcomes.
    login_patch = patch.object(server, "log_in_to_game", return_value=(game_id, user))
    create_game_patch = patch.object(server, "create_game", return_value=AsyncMock())
    main_patch = patch.object(server, "main", new_callable=AsyncMock)

    # Apply patches using the `with` statement to ensure they're correctly applied and removed.
    with login_patch as login_mock, create_game_patch as create_mock, main_patch as main_mock:

        websocket_mock = AsyncMock()

        await server.handler(websocket_mock)

        # Verify all functions were called with correct parameters, orchestrating game setup and entry into main loop.
        login_mock.assert_awaited_once_with(websocket_mock)
        create_mock.assert_awaited_once_with(websocket_mock, game_id, user)
        main_mock.assert_awaited_once_with(websocket_mock, create_mock.return_value)
