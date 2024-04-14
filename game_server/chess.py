import copy
from abc import ABC, abstractmethod
from enum import Enum

import config
from graph import send_result_to_app_server


class Color(Enum):
    """Enumeration representing the color of a chess piece.

    Attributes:
        WHITE (str): The color white of piece
        BLACK (str): The color black of piece
    """

    WHITE = "white"
    BLACK = "black"


def opposite_color(color):
    """Function to return the opposite color of the given color.

    Args:
        color (Color): The color for which the opposite color is to be obtained.

    Returns:
        Color: The opposite color of the given color.
    """
    if color == Color.BLACK:
        return Color.WHITE
    elif color == Color.WHITE:
        return Color.BLACK
    else:
        raise Exception(config.WRONG_COLOR)


def to_chess_notation(position):
    """Function to convert the position to chess notation (e.g., (0, 0) => "a1").

    Args:
        position (tuple): The tuple representing the position on the board.

    Returns:
        str: The chess notation for the given position.
    """
    letter_2 = chr(position[0] + 97)
    number_2 = position[1] + 1
    return f"{letter_2}{number_2}"


class Piece(ABC):
    """Abstract base class for chess pieces.

    Attributes:
        color (Color): The color of the piece (white or black).
        position (tuple): The position of the piece on the board (x, y coordinates).
        position_code (str): The chess notation for the position of the piece.
        last_move (int): The move number in which the piece was last moved.
    """

    rook_steps = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    bishop_steps = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
    royal_steps = [*rook_steps, *bishop_steps]
    knight_steps = [
        [y_step, x_step]
        for x_step in [-2, -1, +1, +2]
        for y_step in [-2, -1, +1, +2]
        if abs(x_step) != abs(y_step)
    ]
    pawn_steps = {Color.BLACK: -1, Color.WHITE: 1}

    def __init__(self, color, position, position_code=None):
        """Initializes a new Piece object."""
        self.color = color
        self.position = position
        self.position_code = position_code
        self.last_move = None

    def __repr__(self) -> str:
        """Returns a string representation of the piece, e.g., "K-w" for a white
        King."""
        return f"{self.__class__.__name__[0]}-{self.color.value[0]}"

    def __str__(self) -> str:
        """Returns a string representation of the piece, e.g., "K-w" for a white
        King."""
        return f"{self.__class__.__name__[0]}-{self.color.value[0]}"

    @abstractmethod
    def available_moves(self):
        """Abstract method that should be implemented by each concrete chess piece
        class.

        It should return a list of all available moves for the current piece written in
        chess notation.
        """
        pass

    def possible_moves(self, steps, board, repeat_steps=True):
        """Get a list of all potential moves for the piece based on given steps.

        Args:
            steps (List[List[int]]): Directions in which the piece can move.
            board (Board): The chessboard instance.
            repeat_steps (bool, optional): If True, repeats steps until blocked
                If False, the piece will move only one step in each direction.
                Defaults to True.

        Returns:
            List[str]: List of potential moves for the piece.

        Note:
            It does not consider illegal moves, such as moves that would leave the
            player's king in check.
            To get only legal moves for the piece, use the `available_moves` method
        """
        x, y = self.position
        list_moves = []
        for step in steps:
            range = 1
            while True:
                new_position = to_chess_notation(
                    (x + range * step[1], y + range * step[0])
                )
                if board.is_in(new_position) and board.is_blank(new_position):
                    list_moves.append(new_position)
                    range += 1
                    if not repeat_steps:
                        break
                elif (
                    board.is_in(new_position)
                    and board[new_position].color != self.color
                ):
                    list_moves.append(new_position)
                    break
                else:
                    break
        return list_moves

    def possible_moves_if_check(self, possible_moves, board):
        """Filters and returns a list of possible moves for the piece that
        do not lead to a position where the current player's king is still under check.

        Args:
            possible_moves (List[str]): Potential moves for the piece.
            board (Board): The current chessboard state.

        Returns:
            List[str]: Moves that protect the king from check.

        Note:
            This method is used only when the current player is under check.
            It filters the possible moves to ensure that the king is not left
            in a check position after the move is made.
        """
        moves = []
        for move in possible_moves:
            potential_board = board.simulate_move(self.position_code, move)
            if not potential_board.is_check(on_color=self.color):
                moves.append(move)
            return moves


class Pawn(Piece):
    """Represents a Pawn piece in the chess game.

    Note:
        - Pawns can move forward one square or two squares on their first move.
        - Pawns can capture diagonally one square ahead.
        - Pawns can be promoted to another piece if they reach the last rank.
    """

    def pawn_moves(self, steps, board):
        """Get possible moves for the Pawn, considering only forward movements.

        Args:
            steps (dict): Movement options for the Pawn based on its color.
            board (Board): The current chessboard state.

        Returns:
            list: Chess notations for possible forward moves for the Pawn.
        """
        x, y = self.position
        new_position = to_chess_notation((x, y + steps[self.color]))
        list_moves = []
        if board.is_in(new_position) and board.is_blank(new_position):
            list_moves.append(new_position)
            if (
                (self.color == Color.BLACK and y == 6)
                or (self.color == Color.WHITE and y == 1)
            ) and board.is_blank(to_chess_notation((x, y + 2 * steps[self.color]))):
                list_moves.append(to_chess_notation((x, y + 2 * steps[self.color])))
        return list_moves

    def pawn_captures(self, steps, board):
        """Get possible capture moves for the Pawn, considering diagonal captures.

        Args:
            steps (dict): Movement options for the Pawn based on its color.
            board (Board): The current chessboard state.

        Returns:
            list: Chess notations for possible diagonal capture moves for the Pawn.
        """

        x, y = self.position
        list_moves = []

        for new_position in [
            (x - 1, y + steps[self.color]),
            (x + 1, y + steps[self.color]),
        ]:
            new_position_code = to_chess_notation(new_position)
            if (
                board.is_in(new_position_code)
                and isinstance(board[new_position_code], Piece)
                and board[new_position_code].color != self.color
            ):
                list_moves.append(new_position_code)

            # check en passant possibility
            alongside_position_code = to_chess_notation((new_position[0], y))
            if (
                board.is_in(new_position_code)
                and isinstance(board[alongside_position_code], Pawn)
                and board[alongside_position_code].color != self.color
                and (
                    (
                        self.color == Color.WHITE
                        and y == 4
                        and board.last_move_black[1] == alongside_position_code
                    )
                    or (
                        self.color == Color.BLACK
                        and y == 3
                        and board.last_move_white[1] == alongside_position_code
                    )
                )
            ):
                list_moves.append(new_position_code)

        return list_moves

    def available_moves(self, board, check=False):
        """Get the available moves for the Pawn on the chessboard.

        Args:
            board (Board): The current state of the chessboard.
            check (bool, optional): If True, considers only legal moves
                that do not expose the King to check.

        Returns:
            list: Chess notations for the Pawn's available moves.
        """
        possible_moves = [
            *self.pawn_moves(self.pawn_steps, board),
            *self.pawn_captures(self.pawn_steps, board),
        ]
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Knight(Piece):
    """Represents a Knight piece in the chess game.

    Note:
        - Knights move in an L-shape: two squares in one direction and one square
          in a perpendicular direction.
        - Knights can jump over other pieces.
        - Knights cannot be blocked by other pieces.
    """

    def __repr__(self):
        """Returns a string representation of the piece, e.g., "N-w" for a white
        Knight."""
        return f"N-{self.color.value[0]}"

    def __str__(self):
        """Returns a string representation of the piece, e.g., "N-w" for a white
        Knight."""
        return f"N-{self.color.value[0]}"

    def available_moves(self, board, check=False):
        """Get the available moves for the Knight on the chessboard.

        Args:
            board (Board): The current state of the chessboard.
            check (bool, optional): If True, considers only legal moves
                that do not expose the King to check.

        Returns:
            list: Chess notations for the Knight's available moves.
        """
        possible_moves = self.possible_moves(
            self.knight_steps, board, repeat_steps=False
        )
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Rook(Piece):
    """Represents a Rook piece in the chess game.

    Note:
        - Rooks can participate in castling if they have not moved before.
    """

    def available_moves(self, board, check=False):
        """Get the available moves for the Rook on the chessboard.

        Args:
            board (Board): The current state of the chessboard.
            check (bool, optional): If True, considers only legal moves
                that do not expose the King to check.

        Returns:
            list: Chess notations for the Rook's available moves.
        """
        possible_moves = self.possible_moves(self.rook_steps, board)
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Bishop(Piece):
    """Represents a Bishop piece in the chess game."""

    def available_moves(self, board, check=False):
        """Get available moves for the Bishop on the chessboard.

        Args:
            board (Board): The current chessboard state.
            check (bool, optional): If True, considers only legal moves
                that do not expose the King to check.

        Returns:
            list: Chess notations for the Bishop's available moves.
        """
        possible_moves = self.possible_moves(self.bishop_steps, board)
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Queen(Piece):
    """Represents a Queen piece in the chess game."""

    def available_moves(self, board, check=False):
        """Get available moves for the Queen on the chessboard.

        Args:
            board (Board): The current chessboard state.
            check (bool, optional): If True, considers only legal moves
                that do not expose the King to check.

        Returns:
            list: Chess notations for the Queen's available moves.
        """
        possible_moves = self.possible_moves(self.royal_steps, board)
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class King(Piece):
    """Represents a King piece in the chess game.

    Note:
        - The King is the most critical piece; the game ends if it's in checkmate.
        - The King can perform castling under certain conditions.
    """

    def available_moves(self, board, check=False):
        """Get available moves for the King on the chessboard.

        Args:
            board (Board): The current chessboard state.
            check (bool, optional): If True, considers only legal moves
                that do not expose the King to check.

        Returns:
            list: Chess notations for the King's available moves.
        """
        possible_moves = self.possible_moves(
            self.royal_steps, board, repeat_steps=False
        )
        for move in reversed(possible_moves):
            potential_board = board.simulate_move(self.position_code, move)
            if potential_board.is_check(on_color=self.color):
                possible_moves.remove(move)

        # check if castling is available and add to list of moves
        if all(
            [
                not self.last_move,
                not board.rook_a[self.color].last_move,
                board.is_blank(f"b{self.position_code[1]}"),
                board.is_blank(f"c{self.position_code[1]}"),
                board.is_blank(f"d{self.position_code[1]}"),
            ]
        ):
            possible_moves.append(f"c{self.position_code[1]}")
        if all(
            [
                not self.last_move,
                not board.rook_h[self.color].last_move,
                board.is_blank(f"g{self.position_code[1]}"),
                board.is_blank(f"f{self.position_code[1]}"),
            ]
        ):
            possible_moves.append(f"g{self.position_code[1]}")

        return possible_moves


class Board:
    """Represents a chessboard in the chess game.

    Attributes:
        gameboard (list): 2D list for the chessboard with pieces.
        all_pieces (dict): Sets of all pieces for each color.
        king (dict): The king piece for each color.
        rook_a (dict): The rook piece for each color on the 'a' file.
        rook_h (dict): The rook piece for each color on the 'h' file.
        record_of_moves (dict): Record of all moves played in the game.
        record_of_gameboard (dict): Records of gameboard states for three-fold
            repetition check.
        fifty_move_count (int): Moves without capture or pawn moves counter.
    """

    def __init__(self):
        """Initializes a new Board object."""
        self.EMPTY = None
        self.gameboard = [8 * [self.EMPTY] for _ in range(8)]
        self.all_pieces = {Color.BLACK: set(), Color.WHITE: set()}
        self.generate_pieces_on_board()
        self.king = {Color.WHITE: self["e1"], Color.BLACK: self["e8"]}
        self.rook_a = {Color.WHITE: self["a1"], Color.BLACK: self["a8"]}
        self.rook_h = {Color.WHITE: self["h1"], Color.BLACK: self["h8"]}
        self.record_of_moves = {0: []}
        self.last_move_black = (None, None)
        self.last_move_white = (None, None)
        self.record_of_gameboard = {"one_rep": [], "two_rep": [], "three_rep": []}
        self.save_gameboard(self.gameboard)
        self.fifty_move_count = 0

    def __getitem__(self, notation):
        """Get a chess piece on the board using chess notation.

        Args:
            notation (str): Position on the board in chess notation.

        Returns:
            Piece or str: Chess piece at the specified position or " " if empty.
        """
        x_idx = ord(notation[0]) - 97
        y_idx = int(notation[1]) - 1
        return self.gameboard[y_idx][x_idx]

    def __setitem__(self, notation, piece):
        """Set a chess piece on the board using chess notation.

        Args:
            notation (str): Position on the board in chess notation.
            piece (Piece or str): Chess piece to be placed or " " to empty the spot.
        """
        x_idx = ord(notation[0]) - 97
        y_idx = int(notation[1]) - 1
        if isinstance(piece, Piece):
            piece.position_code = notation
            piece.position = (x_idx, y_idx)
        self.gameboard[y_idx][x_idx] = piece

    def generate_pieces_on_board(self):
        """Generate and place all pieces on the initial chessboard."""
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for num in range(8):
            # Create and place pieces on their initial positions.
            white_piece = placement[num](Color.WHITE, (num, 7))
            black_piece = placement[num](Color.BLACK, (num, 0))
            white_pawn = Pawn(Color.WHITE, (num, 6))
            black_pawn = Pawn(Color.BLACK, (num, 1))

            # Update the 'all_pieces' dictionary with sets of pieces for each color
            self.all_pieces[Color.WHITE].update({white_piece, white_pawn})
            self.all_pieces[Color.BLACK].update({black_piece, black_pawn})

            # Put pieces on the board
            y_idx = chr(num + 97)  # Converts 'num' to lowercase letter (a-h) in ASCII.
            self[f"{y_idx}7"] = black_pawn
            self[f"{y_idx}8"] = black_piece
            self[f"{y_idx}2"] = white_pawn
            self[f"{y_idx}1"] = white_piece

    def is_no_legal_move(self, on_color, check=False):
        """Check if the player of the specified color has no legal move.

        Args:
            on_color (Color): Color of the player to check for stalemate.
            check (bool, optional): If checking stalemate in a check situation.

        Returns:
            bool: True if no legal move, False otherwise.
        """
        for piece in self.all_pieces[on_color]:
            if piece.available_moves(self, check):
                return False
        return True

    def is_check(self, on_color):
        """Check if the player of the specified color is in check.

        Args:
            on_color (Color): The color of the player to check for check.

        Returns:
            bool: True if the player of the specified color is in check, False otherwise
        """
        king = self.king[on_color]
        attackers = self.all_pieces[opposite_color(on_color)]
        attackers = attackers.difference({self.king[opposite_color(on_color)]})
        for piece in attackers:
            for target in piece.available_moves(self):
                if target == king.position_code:
                    return True
        return False

    def is_blank(self, position):
        """Check if a given position on the board is empty.

        Args:
            position (str or tuple): Position to check in chess notation or tuple.

        Returns:
            bool: True if the position is empty, False otherwise.
        """
        if isinstance(position, str):
            return self[position] == self.EMPTY
        return self.gameboard[position[1]][position[0]] == self.EMPTY

    def is_in(self, position):
        """Check if a given position is within the board's boundaries.

        Args:
            position (str or tuple): Chess notation or tuple representing the position.

        Returns:
            bool: True if the position is within the board's boundaries, False otherwise
        """
        if isinstance(position, str):
            return position[0] in "abcdefgh" and 0 < int(position[1:]) <= 8
        return -1 < position[1] < 8 and -1 < position[0] < 8

    def save_move(self, start_field, end_field, piece):
        """Save the move to record_of_moves made by a piece.

        Args:
            start_field (str): Starting position of the move in chess notation.
            end_field (str): Ending position of the move in chess notation.
            piece (Piece): The chess piece making the move.
        """
        num_move = max(self.record_of_moves.keys())
        piece.last_move = num_move
        if piece.color == Color.WHITE:
            self.record_of_moves[num_move + 1] = [f"{start_field}:{end_field}"]
            self.last_move_white = (start_field, end_field)
        else:
            self.record_of_moves[num_move].append(f"{start_field}:{end_field}")
            self.last_move_black = (start_field, end_field)

    def save_gameboard(self, gameboard):
        """Save the current state of the gameboard for repetition check.

        Args:
            gameboard (list): 2D list representing the chessboard with pieces.
        """
        str_gameboard = [piece.__str__() for row in gameboard for piece in row]
        if str_gameboard in self.record_of_gameboard["two_rep"]:
            self.record_of_gameboard["three_rep"].append(str_gameboard)
        elif str_gameboard in self.record_of_gameboard["one_rep"]:
            self.record_of_gameboard["two_rep"].append(str_gameboard)
        else:
            self.record_of_gameboard["one_rep"].append(str_gameboard)

    def make_move(self, start_field, end_field, simulate_board=None):
        """Make a move on the chessboard.

        Args:
            start_field (str): Chess notation representing the starting move postion
            end_field (str): Chess notation representing the ending move position.
            simulate_board (Board, optional): A simulated board to make the move
                without modifying the original board.

        Note:
            - This function updates the game board with the new piece positions.
            - It checks for pawn promotion and castling moves.
            - If the 'simulate_board' parameter is used, the move is performed on
            the simulated board.
            - The function returns True if the move is valid and False otherwise.
            - The function also updates the move history and the record of game
            board positions.
        """
        # Determine the board to perform the move on
        if simulate_board:
            board = simulate_board
        else:
            board = self

        # Get the pieces at the starting and ending field
        piece = board[start_field]
        target = board[end_field]

        # Check if the piece is a pawn and reset the fifty-move counter if it moves
        if isinstance(piece, Pawn):
            self.fifty_move_count = 0
            # Check if the pawn reached the last rank for promotion
            if (end_field[1] == "8" and piece.color == Color.WHITE) or (
                end_field[1] == "1" and piece.color == Color.BLACK
            ):
                piece = Queen(piece.color)  # pawn promotion

        # If there is a piece at the ending field, remove it from the board
        if isinstance(target, Piece):
            target.position = None
            board.all_pieces[target.color].discard(target)
            if not simulate_board:
                # Reset the fifty-move counter if it is a capturing move
                self.fifty_move_count = 0

        # Check if en passant was made and involved it
        if isinstance(piece, Pawn) and start_field[0] != end_field[0]:
            direct = piece.pawn_steps[piece.color]
            captured_pawn_position = end_field[0] + str(int(end_field[1]) - direct)
            captured_pawn = board[captured_pawn_position]

            board.all_pieces[captured_pawn.color].discard(captured_pawn)
            board[captured_pawn_position] = self.EMPTY

        # Check if the move is castling for the King
        elif isinstance(piece, King) and not piece.last_move:
            row = end_field[1]
            match end_field[0]:
                case "c":
                    board[f"c{row}"] = board[f"e{row}"]
                    board[f"d{row}"] = board[f"a{row}"]
                    board[f"a{row}"] = self.EMPTY
                    board[f"e{row}"] = self.EMPTY
                case "g":
                    board[f"g{row}"] = board[f"e{row}"]
                    board[f"f{row}"] = board[f"h{row}"]
                    board[f"e{row}"] = self.EMPTY
                    board[f"h{row}"] = self.EMPTY
                case _:
                    pass

        # Update the board with the new piece positions
        board[end_field] = piece
        board[start_field] = self.EMPTY

        # If not simulating the move, save the move and update the fifty-move counter
        if not simulate_board:
            self.save_move(start_field, end_field, piece)
            self.save_gameboard(self.gameboard)
            self.fifty_move_count += 1

    def simulate_move(self, start_pos, end_pos):
        """Simulate a move on the chessboard without modifying the original board.

        Args:
            start_pos (str): Chess notation representing the starting move position.
            end_pos (str): Chess notation representing the ending move position.

        Returns:
            Board: A new board representing the state after the simulated move.
        """
        board_copy = copy.deepcopy(self)
        self.make_move(start_pos, end_pos, board_copy)
        return board_copy

    def check_if_legal_move(self, start_field, end_field, current_player):
        """Check if a move is legal for the current player.

        Args:
            start_field (str): Chess notation representing the starting position
                of the move.
            end_field (str): Chess notation representing the ending move position.
            current_player (Player): The current player making the move.

        Raises:
            Exception: If the move is not legal.
        """
        piece = self[start_field]
        check = self.is_check(on_color=current_player.color)
        if piece == self.EMPTY:
            raise Exception(config.EMPTY_START_FIELD)
        if piece.color != current_player.color:
            raise Exception(config.NOT_YOUR_PIECE)
        if end_field not in piece.available_moves(self, check=check):
            raise Exception(
                config.ILLEGAL_MOVE.format(piece.available_moves(self, check=check))
            )

        potential_board = self.simulate_move(start_field, end_field)
        if potential_board.is_check(on_color=current_player.color):
            raise Exception(config.ILLEGAL_MOVE_CHECK_WARNING)

    def check_if_checkmate(self, current_player):
        """Check if the current player is in checkmate.

        Args:
            current_player (Player): The current player to check for checkmate.

        Returns:
            bool: True if the current player is in checkmate, False otherwise.
        """
        if self.is_check(
            on_color=opposite_color(current_player.color)
        ) and self.is_no_legal_move(
            on_color=opposite_color(current_player.color), check=True
        ):
            return True
        return False

    def check_if_stalemate(self, current_player):
        """Check if the current player is in stalemate.

        Args:
            current_player (Player): The current player to check for stalemate.

        Returns:
            str or None: A string describing the type of stalemate, or None if not
                in stalemate.
        """
        if self.is_no_legal_move(on_color=opposite_color(current_player.color)):
            return "Stalemate! No legal move"
        elif self.record_of_gameboard["three_rep"]:
            return "Stalemate! 3-fold repetition"
        elif self.fifty_move_count >= 50:
            return "Stalemate! 50-move rule"


class Player:
    """Represents a player participating in a chess game.

    Attributes:
        websocket (WebSocketServerProtocol): The WebSocket connection associated
            with the player.
        username (str): The username of the player.
        color (Color): The color of the player's pieces
    """

    def __init__(self, websocket, username, color):
        """Initialize a new player with the provided WebSocket, username, and color."""
        self.username = username
        self.websocket = websocket
        self.color = color


class Game:
    """Represents a chess game.

    Attributes:
        board (Board): The chessboard on which the game is played.
        player_1 (Player): The first player participating in the game.
        player_2 (Player): The second player participating in the game.
        winner (Player): The player who has won the game, None if the game is
            ongoing or drawn.
        is_over (bool): True if the game has ended, False otherwise.
        result_description (str): Description of the game result.
        id (int): The unique identifier of the game.
    """

    instances = []  # List to store all created game instances.

    def __init__(self, id):
        self.board = Board()
        self.player_1 = None
        self.player_2 = None
        self.winner = None
        self.is_over = False
        self.result_description = ""
        self.id = id

        # Add this game instance to the list of instances after it's created.
        Game.instances.append(self)

    @classmethod
    def get(cls, id):
        """Get the game instance based on its unique identifier.

        Args:
            id (int): The unique identifier of the game.

        Returns:
            Game or None: The Game instance with the specified ID, or None if not found.
        """
        return next((inst for inst in cls.instances if inst.id == id), None)

    def place_players(self, player_1, player_2):
        """Assign the first and second players to the game.

        Args:
            player_1 (dict): Information about the first player.
            player_2 (dict): Information about the second player.
        """
        self.player_1 = Player(player_1["websocket"], player_1["username"], Color.WHITE)
        self.player_2 = Player(player_2["websocket"], player_2["username"], Color.BLACK)

    def handle_move(self, start_field, end_field, websocket):
        """Handle a move made by a player.

        Args:
            start_field (str): The starting position of the piece to be moved
            end_field (str): The ending position of the piece after the move
            websocket (WebSocketServerProtocol): WebSocket connection of the player
                making the move.

        Note:
            This method is responsible for processing a move made by a player during
            the chess game. It performs various checks to ensure the move is valid,
            including checking if the piece can move to the specified destination, if
            the destination is empty or can be captured, and if the move results in
            checkmate or stalemate. If the move is legal, it updates the game board
            accordingly and sends the result to the app server.
        """
        # Identify the current player based on the WebSocket object
        if self.player_1.websocket == websocket:
            current_player = self.player_1
        elif self.player_2.websocket == websocket:
            current_player = self.player_2
        else:
            raise Exception(config.INVALID_PARTICIPANT)

        # Check if the move is legal and update the game board accordingly
        self.board.check_if_legal_move(start_field, end_field, current_player)
        self.board.make_move(start_field, end_field)
        # Check if the move results in checkmate
        if self.board.check_if_checkmate(current_player):
            result_description = f"Check-Mate! {current_player.username} won!"
            self.end_with_win(current_player, result_description)
        # Check if the move results in stalemate
        if result_description := self.board.check_if_stalemate(current_player):
            self.end_with_draw(result_description)

    def end_with_win(self, current_player, result_description):
        """End the game with a win for the specified player.

        Args:
            current_player (Player): The player who has won the game.
            result_description (str): Description of the game result.
        """
        self.winner = current_player
        self.result_description = result_description
        self.is_over = True
        return send_result_to_app_server(self.winner.username, self.id)

    def end_with_draw(self, result_description):
        """End the game with a draw (stalemate).

        Args:
            result_description (str): Description of the game result.
        """
        self.result_description = result_description
        self.is_over = True
        return send_result_to_app_server("", self.id)

    def get_chessboard(self, websocket):
        """Get the current chessboard as a string representation for the specified
        player.

        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection of the player.

        Returns:
            str: Object representation of the chessboard.
        """

        board_strings = [
            [str(piece) if piece else None for piece in row]
            for row in self.board.gameboard
        ]

        if self.player_1.websocket == websocket:
            return board_strings[::-1]
        else:
            return [row[::-1] for row in board_strings]
