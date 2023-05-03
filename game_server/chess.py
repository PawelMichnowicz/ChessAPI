import copy
from abc import ABC, abstractmethod

from enum import Enum
from graph import send_result

EMPTY = " "


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


def opposite_color(color):
    if color == Color.BLACK:
        return Color.WHITE
    elif color == Color.WHITE:
        return Color.BLACK
    else:
        raise Exception("Invalid color")


def to_chess_notation(position):
    letter_2 = chr(position[0] + 97)
    number_2 = position[1] + 1
    return f"{letter_2}{number_2}"


class Piece(ABC):
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
        self.color = color
        self.position = position
        self.position_code = position_code
        self.last_move = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__[0]}-{self.color.value[0]}"

    def __str__(self) -> str:
        return f"{self.__class__.__name__[0]}-{self.color.value[0]}"

    @abstractmethod
    def available_moves(self):
        pass

    def possible_moves(self, steps, board, repeat_steps=True):
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
        moves = []
        for move in possible_moves:
            potential_board = board.simulate_move(self.position_code, move)
            if not potential_board.is_check(on_color=self.color):
                moves.append(move)
            return moves

    def pawn_moves(self, steps, board):
        x, y = self.position
        list_moves = []
        new_position = to_chess_notation((x, y + steps[self.color]))
        if board.is_in(new_position) and board.is_blank(new_position):
            list_moves.append(new_position)
            if (
                (self.color == Color.BLACK and y == 6)
                or (self.color == Color.WHITE and y == 1)
            ) and board.is_blank(to_chess_notation((x, y + 2 * steps[self.color]))):
                list_moves.append(to_chess_notation((x, y + 2 * steps[self.color])))
        return list_moves

    def pawn_captures(self, steps, board):
        x, y = self.position
        list_moves = []
        for new_position in [
            (x - 1, y + steps[self.color]),
            (x + 1, y + steps[self.color]),
        ]:
            new_position = to_chess_notation(new_position)
            if (
                board.is_in(new_position)
                and not board.is_blank(new_position)
                and board[new_position].color != self.color
            ):
                list_moves.append(new_position)
        return list_moves


class Pawn(Piece):
    def available_moves(self, board, check=False):
        possible_moves = [
            *self.pawn_moves(self.pawn_steps, board),
            *self.pawn_captures(self.pawn_steps, board),
        ]
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Knight(Piece):
    def __repr__(self):
        return f"N-{self.color.value[0]}"

    def __str__(self):
        return f"N-{self.color.value[0]}"

    def available_moves(self, board, check=False):
        possible_moves = self.possible_moves(
            self.knight_steps, board, repeat_steps=False
        )
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Rook(Piece):
    def available_moves(self, board, check=False):
        possible_moves = self.possible_moves(self.rook_steps, board)
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Bishop(Piece):
    def available_moves(self, board, check=False):
        possible_moves = self.possible_moves(self.bishop_steps, board)
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Queen(Piece):
    def available_moves(self, board, check=False):
        possible_moves = self.possible_moves(self.royal_steps, board)
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class King(Piece):
    def available_moves(self, board, check=False):
        possible_moves = self.possible_moves(
            self.royal_steps, board, repeat_steps=False
        )
        for move in possible_moves:
            potential_board = board.simulate_move(self.position_code, move)
            if potential_board.is_check(on_color=self.color):
                possible_moves.remove(move)

        # check possible castling
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
    def __init__(self):
        self.gameboard = [8 * [EMPTY] for _ in range(8)]
        self.all_pieces = {Color.BLACK: set(), Color.WHITE: set()}
        self.generate_pieces_on_board()
        self.king = {Color.WHITE: self["e1"], Color.BLACK: self["e8"]}
        self.rook_a = {Color.WHITE: self["a1"], Color.BLACK: self["a8"]}
        self.rook_h = {Color.WHITE: self["h1"], Color.BLACK: self["h8"]}
        self.record_of_moves = {0: []}
        self.record_of_gameboard = {"one_rep": [], "two_rep": [], "three_rep": []}
        self.save_gameboard(self.gameboard)
        self.fifty_move_count = 0

    def __getitem__(self, notation):
        x_idx = ord(notation[0]) - 97
        y_idx = int(notation[1]) - 1
        return self.gameboard[y_idx][x_idx]

    def __setitem__(self, notation, piece):
        x_idx = ord(notation[0]) - 97
        y_idx = int(notation[1]) - 1
        if isinstance(piece, Piece):
            piece.position_code = notation
            piece.position = (x_idx, y_idx)
        self.gameboard[y_idx][x_idx] = piece

    def generate_pieces_on_board(self):
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for num in range(8):
            white_piece = placement[num](Color.WHITE, (num, 7))
            black_piece = placement[num](Color.BLACK, (num, 0))
            white_pawn = Pawn(Color.WHITE, (num, 6))
            black_pawn = Pawn(Color.BLACK, (num, 1))
            self.all_pieces[Color.WHITE].update({white_piece, white_pawn})
            self.all_pieces[Color.BLACK].update({black_piece, black_pawn})
            y_idx = chr(num + 97)
            self[f"{y_idx}7"] = black_pawn
            self[f"{y_idx}8"] = black_piece
            self[f"{y_idx}2"] = white_pawn
            self[f"{y_idx}1"] = white_piece

    def print_board(self):
        for line in self.gameboard[::-1]:
            print(line)

    def is_stalemate(self, on_color, check=False):
        for piece in self.all_pieces[on_color]:
            if piece.available_moves(self, check):
                return False
        return True

    def is_check(self, on_color):
        king = self.king[on_color]
        attackers = self.all_pieces[opposite_color(on_color)]
        attackers = attackers.difference({self.king[opposite_color(on_color)]})
        for piece in attackers:
            for target in piece.available_moves(self):
                if target == king.position_code:
                    return True
        return False

    def is_blank(self, position):
        if isinstance(position, str):
            return self[position] == EMPTY
        return self.gameboard[position[1]][position[0]] == EMPTY

    def is_in(self, position):
        if isinstance(position, str):
            return position[0] in "abcdefgh" and 0 < int(position[1:]) <= 8
        return -1 < position[1] < 8 and -1 < position[0] < 8

    def save_move(self, start_field, end_field, piece):
        num_move = max(self.record_of_moves.keys())
        piece.last_move = num_move
        if piece.color == Color.WHITE:
            self.record_of_moves[num_move + 1] = [f"{start_field}:{end_field}"]
        else:
            self.record_of_moves[num_move].append(f"{start_field}:{end_field}")

    def save_gameboard(self, gameboard):
        str_gameboard = [piece.__str__() for row in gameboard for piece in row]
        if str_gameboard in self.record_of_gameboard["two_rep"]:
            self.record_of_gameboard["three_rep"].append(str_gameboard)
        elif str_gameboard in self.record_of_gameboard["one_rep"]:
            self.record_of_gameboard["two_rep"].append(str_gameboard)
        else:
            self.record_of_gameboard["one_rep"].append(str_gameboard)

    def make_move(self, start_field, end_field, simulate_board=None):
        if simulate_board:
            board = simulate_board
        else:
            board = self

        piece = board[start_field]
        target = board[end_field]
        if isinstance(piece, Pawn):
            self.fifty_move_count = 0
            if (end_field[1] == "8" and piece.color == Color.WHITE) or (
                end_field[1] == "1" and piece.color == Color.BLACK
            ):
                piece = Queen(piece.color)  # pawn promotion
        if isinstance(target, Piece):  # if take piece
            target.position = None
            board.all_pieces[target.color].discard(target)
            if not simulate_board:
                self.fifty_move_count = 0
        elif isinstance(piece, King) and not piece.last_move:  # if castling
            row = end_field[1]
            match end_field[0]:
                case "c":
                    board[f"c{row}"] = board[f"e{row}"]
                    board[f"d{row}"] = board[f"a{row}"]
                    board[f"a{row}"] = EMPTY
                    board[f"e{row}"] = EMPTY
                case "g":
                    board[f"g{row}"] = board[f"e{row}"]
                    board[f"f{row}"] = board[f"h{row}"]
                    board[f"e{row}"] = EMPTY
                    board[f"h{row}"] = EMPTY
                case _:
                    pass
        board[end_field] = piece
        board[start_field] = EMPTY

        if not simulate_board:
            self.save_move(start_field, end_field, piece)
            self.save_gameboard(self.gameboard)
            self.fifty_move_count += 1
        return True

    def simulate_move(self, start_pos, end_pos):
        board_copy = copy.deepcopy(self)
        self.make_move(start_pos, end_pos, board_copy)
        return board_copy

    def check_if_legal_move(self, start_field, end_field, current_player):
        piece = self[start_field]
        check = self.is_check(on_color=current_player.color)
        if piece == EMPTY:
            raise Exception("That is empty field!")
        if piece.color != current_player.color:
            raise Exception("It is not your piece!")
        if end_field not in piece.available_moves(self, check=check):
            raise Exception(
                f"Invalid move! Possibilities of this piece: {piece.available_moves(self, check=check)}"
            )

        potential_board = self.simulate_move(start_field, end_field)
        if potential_board.is_check(on_color=current_player.color):
            raise Exception("Illegal move due to attack on your king")

    def check_if_checkmate(self, current_player):
        if self.is_check(
            on_color=opposite_color(current_player.color)
        ) and self.is_stalemate(
            on_color=opposite_color(current_player.color), check=True
        ):
            return True
        return False

    def check_if_stalemate(self, current_player):
        if self.is_stalemate(on_color=opposite_color(current_player.color)):
            return "Stalemate! No legal move"
        elif self.record_of_gameboard["three_rep"]:
            return "Stalemate! 3-fold repetition"
        elif self.fifty_move_count >= 3:
            return "Stalemate! 50-move rule"


class Player:
    def __init__(self, websocket, username, color):
        self.username = username
        self.websocket = websocket
        self.color = color


class Game:
    instances = []

    def __init__(self, id):
        self.board = Board()
        self.player_1 = None
        self.player_2 = None
        self.winner = None
        self.is_over = False
        self.result_description = ""
        self.id = id
        Game.instances.append(self)

    @classmethod
    def get(cls, id):
        return [inst for inst in cls.instances if inst.id == id]

    def place_players(self, player_1, player_2):
        self.player_1 = Player(player_1["websocket"], player_1["username"], Color.WHITE)
        self.player_2 = Player(player_2["websocket"], player_2["username"], Color.BLACK)

    def handle_move(self, start_field, end_field, websocket):
        if self.player_1.websocket == websocket:
            current_player = self.player_1
        elif self.player_2.websocket == websocket:
            current_player = self.player_2
        else:
            raise Exception("You are not a participant of game")

        self.board.check_if_legal_move(start_field, end_field, current_player)
        self.board.make_move(start_field, end_field)
        if self.board.check_if_checkmate(current_player):
            result_description = f"Check-Mate! {current_player.username} won!"
            self.end_with_win(current_player, result_description)
        if result_description := self.board.check_if_stalemate(current_player):
            self.end_with_draw(result_description)

    def end_with_win(self, current_player, result_description):
        self.winner = current_player
        self.result_description = result_description
        self.is_over = True
        return send_result(self.winner.username, self.id)

    def end_with_draw(self, result_description):
        self.result_description = result_description
        self.is_over = True
        return send_result("", self.id)

    def get_chessboard(self, websocket):
        board_string = ""
        direct = 1
        if self.player_1.websocket == websocket:
            direct = -1
        for line in self.board.gameboard[::direct]:
            board_string += str(line)
            board_string += "\n"
        return board_string
