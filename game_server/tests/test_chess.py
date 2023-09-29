import pytest
from unittest.mock import Mock, patch

import config
from chess import Bishop, Board, Color, Game, King, Knight, Pawn, Player, Queen, Rook


@pytest.fixture
def game():
    """
    Fixture to initialize a test instance of the Game class.

    This fixture can be used as a parameter in tests that require a preconfigured game instance.

    Returns:
        Game: An instance of the Game class representing a preconfigured test game.
    """
    game = Game("test_id")
    game.player_1 = Player("websocket_white", "white", Color.WHITE)
    game.player_2 = Player("websocket_black", "black", Color.BLACK)
    return game


@pytest.fixture
def game_with_empty_board():
    """
    Fixture to initialize a test instance of the Game class with an empty chessboard.

    This fixture can be used as a parameter in tests that require a preconfigured game instance with an empty chessboard, allowing for custom piece placement during the test.

    Returns:
        Game: An instance of the Game class representing a test game with an empty chessboard.
    """
    game = Game("test_id")
    game.player_1 = Player("websocket_white", "white", Color.WHITE)
    game.player_2 = Player("websocket_black", "black", Color.BLACK)
    game.board.all_pieces = {Color.BLACK: set(), Color.WHITE: set()}
    game.board.gameboard = [8 * [game.board.EMPTY] for _ in range(8)]
    game.board.king = {Color.WHITE: None, Color.BLACK: None}
    return game


def put_piece_on_board(board, piece_class, color, position):
    """
    Helper function to place a chess piece on the board at a specified position.

    This function creates an instance of a specified chess piece class with the given color and places it on the
    chessboard at the specified position. Additionally, it updates the set of all pieces of the given color.

    Args:
        board (Board): The chessboard instance.
        piece_class (class): The class of the chess piece to be placed.
        color (Color): The color of the chess piece (Color.WHITE or Color.BLACK).
        position (str): The algebraic notation of the position on the chessboard (e.g3, "a1", "b2").
    """
    y_idx = ord(position[0]) - 97
    x_idx = int(position[1]) - 1
    piece = piece_class(color, (x_idx, y_idx))
    board.all_pieces[color].add(piece)
    board[position] = piece
    if piece_class == King:
        board.king[color] = piece


def test_setting_initial_board():
    """
    Test case for setting up the initial chessboard.

    This function checks if the initial configuration of the chessboard is set up correctly by verifies the correct setup of pieces in specific positions on the chessboard.
    """
    board = Board()
    assert vars(board["a2"]) == vars(Pawn(Color.WHITE, (0, 1), "a2"))
    assert vars(board["a7"]) == vars(Pawn(Color.BLACK, (0, 6), "a7"))
    assert vars(board["a8"]) == vars(Rook(Color.BLACK, (0, 7), "a8"))
    assert vars(board["b1"]) == vars(Knight(Color.WHITE, (1, 0), "b1"))
    assert vars(board["c1"]) == vars(Bishop(Color.WHITE, (2, 0), "c1"))
    assert vars(board["f8"]) == vars(Bishop(Color.BLACK, (5, 7), "f8"))
    assert vars(board["e8"]) == vars(King(Color.BLACK, (4, 7), "e8"))


def test_valid_castling(game):
    """
    Test cases for valid castling moves in a chess game.

    This function tests two valid castling scenarios:
    1. Castling on the queen side for the white player.
    2. Castling on the king side for the black player.
    """
    # test castling on the queen side (white color)
    game.handle_move("b1", "a3", "websocket_white")
    game.handle_move("d2", "d4", "websocket_white")
    game.handle_move("c1", "e3", "websocket_white")
    game.handle_move("d1", "d3", "websocket_white")
    game.handle_move("e1", "c1", "websocket_white")
    assert vars(game.board["d1"]) == vars(Rook(Color.WHITE, (3, 0), "d1"))

    # test castling on the king side (black color)
    game.handle_move("g8", "h6", "websocket_black")
    game.handle_move("e7", "e6", "websocket_black")
    game.handle_move("f8", "e7", "websocket_black")
    game.handle_move("e8", "g8", "websocket_black")
    assert vars(game.board["f8"]) == vars(Rook(Color.BLACK, (5, 7), "f8"))


def test_invalid_castling(game):
    """
    Test cases for invalid castling moves in a chess game.

    This function tests two types of invalid castling scenarios:
    1. Castling with pieces between the rook and king.
    2. Castling when the king or rook involved has already moved.
    """
    # Invalid because pieces between rook and king
    with pytest.raises(Exception) as exc_info:
        game.handle_move("e1", "c1", "websocket_white")
        game.handle_move("e8", "g8", "websocket_black")
    assert str(exc_info.value).startswith(config.ILLEGAL_MOVE[:-3])

    # Invalid becouse king or rook already moved, checked king's side
    game.handle_move("g1", "h3", "websocket_white")
    game.handle_move("e2", "e4", "websocket_white")
    game.handle_move("f1", "e2", "websocket_white")
    game.handle_move("h1", "g1", "websocket_white")
    game.handle_move("g1", "h1", "websocket_white")
    with pytest.raises(Exception) as exc_info:
        game.handle_move("e1", "g1", "websocket_white")
    assert str(exc_info.value).startswith(config.ILLEGAL_MOVE[:-3])

    # Invalid becouse king or rook already moved, checked queen's side
    game.handle_move("b8", "a6", "websocket_black")
    game.handle_move("d7", "d5", "websocket_black")
    game.handle_move("c8", "e6", "websocket_black")
    game.handle_move("d8", "d6", "websocket_black")
    game.handle_move("e8", "d8", "websocket_black")
    game.handle_move("d8", "e8", "websocket_black")
    with pytest.raises(Exception) as exc_info:
        game.handle_move("e8", "c8", "websocket_black")
    assert str(exc_info.value).startswith(config.ILLEGAL_MOVE[:-3])


def test_pieces_available_moves(game_with_empty_board):
    """
    Test the 'available_moves' method of chess pieces in a specific game scenario.

    The test sets up a chessboard with various pieces of different types and colors.
    It then verifies that the 'available_moves' method of each piece returns the expected valid moves.

    Visual representation of the initial chessboard setup:
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', K-b]
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', P-w]
    [' ', ' ', ' ', ' ', ' ', ' ', N-b, ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', P-w, P-b, ' ', ' ', ' ', ' ', ' ']
    [P-w, P-w, B-b, ' ', ' ', ' ', ' ', ' ']
    [K-w, Q-w, ' ', ' ', ' ', ' ', ' ', R-b]
    """
    game = game_with_empty_board
    put_piece_on_board(game.board, King, Color.BLACK, "h8")
    game.board["h8"].last_move = 1
    put_piece_on_board(game.board, King, Color.WHITE, "a1")
    game.board["a1"].last_move = 1
    put_piece_on_board(game.board, Queen, Color.WHITE, "b1")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "a2")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "b2")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "b3")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "h7")
    put_piece_on_board(game.board, Pawn, Color.BLACK, "c3")
    put_piece_on_board(game.board, Rook, Color.BLACK, "h1")
    put_piece_on_board(game.board, Bishop, Color.BLACK, "c2")
    put_piece_on_board(game.board, Knight, Color.BLACK, "g6")

    expected_moves = {
        "h8": sorted(["h7", "g7"]),
        "a1": [],
        "b1": sorted(["c1", "d1", "e1", "f1", "g1", "h1", "c2"]),
        "a2": sorted(["a3", "a4"]),
        "b2": sorted(["c3"]),
        "b3": sorted(["b4"]),
        "h7": sorted([]),
        "c3": sorted(["b2"]),
        "h1": sorted(
            ["g1", "f1", "e1", "d1", "c1", "b1", "h2", "h3", "h4", "h5", "h6", "h7"]
        ),
        "c2": sorted(["d3", "e4", "f5", "b3", "b1", "d1"]),
        "g6": sorted(["e5", "e7", "f4", "f8", "h4"]),
    }

    for piece_position, expected_move in expected_moves.items():
        assert (
            sorted(game.board[piece_position].available_moves(game.board))
            == expected_move
        )


def test_illegal_moves(game_with_empty_board):
    """
    Test case for validating an illegal move attempted against chess rules

    Visual representation of the initial chessboard setup:
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', K-b]
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [K-w, ' ', B-w, Q-b, ' ', ' ', ' ', ' ']

    Scenarios:
    1. Illegal move attempted by a pinned piece in a chess game.
    2. An opponent's pawn captures en passant immediately after the double move.

    Note:
    - Pinned pieces cannot move in a direction that exposes the king to check.
    """

    # setup initial chessboard
    game = game_with_empty_board
    put_piece_on_board(game.board, King, Color.BLACK, "h8")
    game.board["h8"].last_move = 1
    put_piece_on_board(game.board, King, Color.WHITE, "a1")
    game.board["a1"].last_move = 1
    put_piece_on_board(game.board, Queen, Color.BLACK, "d1")
    put_piece_on_board(game.board, Bishop, Color.WHITE, "c1")

    with patch("chess.send_result_to_app_server", return_value=None):
        # Expected error due to attack on white king
        with pytest.raises(Exception) as exc_info:
            game.handle_move("c1", "d2", "websocket_white")
        assert str(exc_info.value) == config.ILLEGAL_MOVE_CHECK_WARNING

        # Expected error because started field is empty
        with pytest.raises(Exception) as exc_info:
            game.handle_move("a2", "d2", "websocket_white")
        assert str(exc_info.value) == config.EMPTY_START_FIELD

        # Expected error because the figure does not belong to the player
        with pytest.raises(Exception) as exc_info:
            game.handle_move("a1", "d2", "websocket_black")
        assert str(exc_info.value) == config.NOT_YOUR_PIECE


@pytest.mark.parametrize(
    ("start_field", "end_field"),
    [
        ("a3", "c2"),
        ("d1", "b1"),
    ],
)
def test_checkmate(start_field, end_field, game_with_empty_board):
    """
    Test the checkmate scenario in a chess game.

    This test covers two types of checkmate scenarios:
    1. Classic checkmate scenario. ("a3", "c2")
    2. Checkmate scenario involving a pinned piece preventing the capture of the attacking king. ("d1", "b1")

    Visual representation of the initial chessboard setup:
    [' ', ' ', K-b, ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [N-b, ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [P-w, P-w, ' ', ' ', ' ', ' ', ' ', ' ']
    [K-w, B-w, ' ', Q-b, ' ', ' ', ' ', ' ']

    Parameters:
    - start_field (str): The starting position of the piece making the move.
    - end_field (str): The target position for the piece making the move.
    """

    # setup initial chessboard
    game = game_with_empty_board
    put_piece_on_board(game.board, King, Color.BLACK, "c8")
    game.board["c8"].last_move = 1
    put_piece_on_board(game.board, King, Color.WHITE, "a1")
    game.board["a1"].last_move = 1
    put_piece_on_board(game.board, Pawn, Color.WHITE, "b2")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "a2")
    put_piece_on_board(game.board, Bishop, Color.WHITE, "b1")
    put_piece_on_board(game.board, Queen, Color.BLACK, "d1")
    put_piece_on_board(game.board, Knight, Color.BLACK, "a3")

    # Mock the send_result_to_app_server function
    with patch("chess.send_result_to_app_server", return_value=None):
        game.handle_move(start_field, end_field, "websocket_black")
    assert game.is_over
    assert game.winner == game.player_2
    assert game.board.check_if_checkmate(game.player_2)


def test_stalemate_repetition(game_with_empty_board):
    """
    Test case for checking stalemate where stalemate occurs due to repeated positions.

    Visual representation of the initial chessboard setup:
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', K-b]
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [Q-b, ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [P-w, P-w, ' ', R-w, ' ', ' ', ' ', ' ']
    [K-w, ' ', ' ', ' ', ' ', ' ', ' ', ' ']

    Note:
    - Stalemate by repetition occurs when the same position is repeated three times.
    """

    # setup initial chessboard
    game = game_with_empty_board
    put_piece_on_board(game.board, King, Color.BLACK, "h8")
    game.board["h8"].last_move = 1
    put_piece_on_board(game.board, Queen, Color.BLACK, "a3")
    put_piece_on_board(game.board, King, Color.WHITE, "a1")
    game.board["a1"].last_move = 1
    put_piece_on_board(game.board, Pawn, Color.WHITE, "a2")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "b2")
    put_piece_on_board(game.board, Rook, Color.WHITE, "d2")

    # Mock the send_result_to_app_server function
    with patch("chess.send_result_to_app_server", return_value=None):
        game.handle_move("a1", "b1", "websocket_white")

        game.handle_move("a3", "b3", "websocket_black")
        game.handle_move("d2", "e2", "websocket_white")
        game.handle_move("b3", "a3", "websocket_black")
        game.handle_move("e2", "d2", "websocket_white")

        game.handle_move("a3", "b3", "websocket_black")
        game.handle_move("d2", "e2", "websocket_white")
        game.handle_move("b3", "a3", "websocket_black")
        game.handle_move("e2", "d2", "websocket_white")

    assert game.is_over
    assert not game.winner
    assert game.board.check_if_stalemate(game.player_1)


def test_stalemate_50move_rule(game_with_empty_board):
    """
    Test case for checking stalemate due to the 50-move rule in a chess game.

    Visual representation of the initial chessboard setup:
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', K-b]
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', P-b, ' ', ' ', ' ', ' ']
    [Q-b, ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [P-w, P-w, ' ', R-w, ' ', ' ', ' ', ' ']
    [K-w, ' ', ' ', ' ', ' ', ' ', ' ', ' ']

    Scenarios:
    1. After a move, the move count increases.
    2. Move counting is reset to zero after a pawn move.
    3. Move counting is reset to zero after capturing a piece.
    4. The game ends in a draw after reaching the 50-move rule.

    Note:
    - The 50-move rule states that a player can claim a draw if no pawn has been moved and no piece has been
      captured in the last 50 moves by each player.
    """

    # setup initial chessboard
    game = game_with_empty_board
    put_piece_on_board(game.board, King, Color.BLACK, "h8")
    game.board["h8"].last_move = 1
    put_piece_on_board(game.board, Queen, Color.BLACK, "a3")
    put_piece_on_board(game.board, King, Color.WHITE, "a1")
    game.board["a1"].last_move = 1
    put_piece_on_board(game.board, Pawn, Color.WHITE, "a2")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "b2")
    put_piece_on_board(game.board, Rook, Color.WHITE, "d2")
    put_piece_on_board(game.board, Pawn, Color.BLACK, "d4")

    # Mock the send_result_to_app_server function
    with patch("chess.send_result_to_app_server", return_value=None):
        game.board.fifty_move_count = 40
        game.handle_move("a3", "b3", "websocket_black")
        assert game.board.fifty_move_count == 41

        # reset move counting to zero because pawn's move
        game.handle_move("d4", "d3", "websocket_black")
        assert game.board.fifty_move_count == 1

        # reset move counting to zero because of captured piece
        game.handle_move("d2", "d3", "websocket_white")
        assert game.board.fifty_move_count == 1

        # end game with draw because of 50 move rule
        game.board.fifty_move_count = 49
        assert not game.is_over
        game.handle_move("d3", "d4", "websocket_white")
        assert game.is_over
        assert not game.winner


def test_stalemate_no_legal_move(game_with_empty_board):
    """
    Test case for checking stalemate in a chess game when the player has no legal moves.

    Visual representation of the initial chessboard setup:
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', K-b]
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [K-w, ' ', ' ', ' ', ' ', ' ', Q-w, ' ']

    Note:
    - Stalemate occurs when a player has no legal moves, and their king is not in check.
    """

    # setup initial chessboard
    game = game_with_empty_board
    put_piece_on_board(game.board, Queen, Color.WHITE, "g1")
    put_piece_on_board(game.board, King, Color.WHITE, "a1")
    game.board["a1"].last_move = 1
    put_piece_on_board(game.board, King, Color.BLACK, "h8")
    game.board["h8"].last_move = 1

    with patch("chess.send_result_to_app_server", return_value=None):
        game.handle_move("g1", "g6", "websocket_white")

    assert game.is_over
    assert not game.winner


def test_en_passant(game_with_empty_board):
    """
    Test case for validating the en passant rule in a chess game.

    Visual representation of the initial chessboard setup:
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', K-b]
    [' ', P-b, ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [' ', ' ', P-w, P-b, ' ', ' ', ' ', ' ']
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [Q-b, ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [P-w, ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    [K-w, ' ', ' ', ' ', ' ', ' ', ' ', ' ']

    Scenarios:
    1. En passant capture is not allowed because the opponent's last move was not a double square pawn move.
    2. An opponent's pawn captures en passant immediately after the double move.

    Note:
    - The en passant rule allows a pawn to capture an opponent's pawn that has moved two squares forward from its starting position, as if it had only moved one square forward.
    - En passant capture must be executed immediately after the double square pawn move.
    """

    # setup initial chessboard
    game = game_with_empty_board
    put_piece_on_board(game.board, King, Color.BLACK, "h8")
    game.board["h8"].last_move = 1
    put_piece_on_board(game.board, Queen, Color.BLACK, "a3")
    put_piece_on_board(game.board, King, Color.WHITE, "a1")
    game.board["a1"].last_move = 1
    put_piece_on_board(game.board, Pawn, Color.WHITE, "a2")
    put_piece_on_board(game.board, Queen, Color.BLACK, "a3")
    put_piece_on_board(game.board, Pawn, Color.BLACK, "b7")
    put_piece_on_board(game.board, Pawn, Color.WHITE, "c5")
    put_piece_on_board(game.board, Pawn, Color.BLACK, "d5")

    with patch("chess.send_result_to_app_server", return_value=None):
        game.handle_move("b7", "b5", "websocket_black")

        # Expected error becouse pawn from c5 wasn't opponent's last move
        with pytest.raises(Exception) as exc_info:
            game.handle_move("d5", "c4", "websocket_black")
        assert str(exc_info.value).startswith(config.ILLEGAL_MOVE[:-3])

        num_of_black_pieces = len(game.board.all_pieces[Color.BLACK])
        game.handle_move("c5", "b6", "websocket_white")

    assert game.board["b5"] == game.board.EMPTY
    assert num_of_black_pieces - 1 == len(game.board.all_pieces[Color.BLACK])
