import copy

WHITE = 'white'
BLACK = 'black'

EMPTY = ' '

# szach z odsłony - done
# pat i szach-mat - done
# promocja pionka
# Obsługa notyfikacji szachowej - done
# zapis ruchów
# roszada
# bicie w przelocie
# zasada 50ruchów
# 3krotne powtórzenie


def opposite_color(color):
    if color == BLACK:
        return WHITE
    elif color == WHITE:
        return BLACK
    else:
        raise Exception('Invalid color')


def to_chess_notation(position):

    letter_2 = chr(position[0] + 97)
    number_2 = position[1] + 1
    return f'{letter_2}{number_2}'


class Piece():

    rook_steps = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    bishop_steps = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
    royal_steps = [*rook_steps, *bishop_steps]
    knight_steps = [[y_step, x_step] for x_step in [-2, -1, +1, +2]
                    for y_step in [-2, -1, +1, +2] if abs(x_step) != abs(y_step)]
    pawn_steps = {BLACK: -1, WHITE: 1}

    def __init__(self, color, position, position_code=None):
        self.color = color
        self.position = position
        self.position_code = position_code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__[0]}-{self.color[0]}"

    def __str__(self) -> str:
        return f'{self.__class__.__name__}-{self.color[0].upper()} {self.position_code}'

    def possible_moves(self, steps, board, repeat_steps=True):
        x, y = self.position
        list_moves = []
        for step in steps:
            range = 1
            while True:
                new_position = to_chess_notation(
                    (x+range*step[1], y+range*step[0]))
                if board.is_in(new_position) and board.is_blank(new_position):
                    list_moves.append(new_position)
                    range += 1
                    if not repeat_steps:
                        break
                elif board.is_in(new_position) and board[new_position].color != self.color:
                    list_moves.append(new_position)
                    break
                else:
                    break
        return list_moves

    def pawn_moves(self, steps, board):
        x, y = self.position
        list_moves = []
        new_position = to_chess_notation((x, y+steps[self.color]))
        if board.is_in(new_position) and board.is_blank(new_position):
            list_moves.append(new_position)
            if ((self.color == BLACK and y == 6) or (self.color == WHITE and y == 1)) and\
                    board.is_blank(to_chess_notation((x, y+2*steps[self.color]))):
                list_moves.append(to_chess_notation(
                    (x, y+2*steps[self.color])))
        return list_moves

    def pawn_captures(self, steps, board):
        x, y = self.position
        list_moves = []
        for new_position in [(x-1, y+steps[self.color]), (x+1, y+steps[self.color])]:
            new_position = to_chess_notation(new_position)
            if board.is_in(new_position) and not board.is_blank(new_position) and board[new_position].color != self.color:
                list_moves.append(new_position)
        return list_moves

    def possible_moves_if_check(self, possible_moves, board):
        moves = []
        for move in possible_moves:
            potential_board = board.simulate_move(self.position_code, move)
            if not potential_board.is_check(on_color=self.color):
                moves.append(move)
            return moves


class Pawn(Piece):

    def available_moves(self, board, check=False):
        possible_moves = [
            *self.pawn_moves(self.pawn_steps, board), *self.pawn_captures(self.pawn_steps, board)]
        if not check:
            return possible_moves
        return self.possible_moves_if_check(possible_moves, board)


class Knight(Piece):

    def __repr__(self):
        return f'N-{self.color[0]}'

    def available_moves(self, board, check=False):
        possible_moves = self.possible_moves(
            self.knight_steps, board, repeat_steps=False)
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
        possible_moves = self.possible_moves(self.royal_steps, board, repeat_steps=False)
        for move in possible_moves:
            potential_board = board.simulate_move(self.position_code, move)
            if potential_board.is_check(on_color=self.color):
                possible_moves.remove(move)
        return possible_moves


class Board(object):

    def __init__(self):

        self.gameboard = [8*[EMPTY] for _ in range(8)]
        self.all_pieces = {BLACK: set(), WHITE: set()}
        self.generate_pieces_on_board()
        self.king = {WHITE: self['e1'], BLACK: self['e8']}

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
            white_piece = placement[num](WHITE, (num, 7))
            black_piece = placement[num](BLACK, (num, 0))
            white_pawn = Pawn(WHITE, (num, 6))
            black_pawn = Pawn(BLACK, (num, 1))
            self.all_pieces[WHITE].update({white_piece, white_pawn})
            self.all_pieces[BLACK].update({black_piece, black_pawn})
            y_idx = chr(num+97)
            self[f'{y_idx}7'] = black_pawn
            self[f'{y_idx}8'] = black_piece
            self[f'{y_idx}2'] = white_pawn
            self[f'{y_idx}1'] = white_piece

    def print_board(self):
        for line in self.gameboard:
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

    def is_blank(self, position):  # here
        if isinstance(position, str):
            return self[position] == EMPTY
        return self.gameboard[position[1]][position[0]] == EMPTY

    def is_in(self, position):
        if isinstance(position, str):
            return position[0] in 'abcdefgh' and 0 < int(position[1:]) <= 8
        return -1 < position[1] < 8 and -1 < position[0] < 8

    def make_move(self, start_pos, end_pos, test_board=None):
        if test_board:
            board = test_board
        else:
            board = self

        piece = board[start_pos]
        target = board[end_pos]

        if isinstance(target, Piece):
            target.position = None
            board.all_pieces[target.color].discard(target)
        board[end_pos] = piece
        board[start_pos] = EMPTY
        return True

    def simulate_move(self, start_pos, end_pos):
        board_copy = copy.deepcopy(self)
        self.make_move(start_pos, end_pos, board_copy)
        return board_copy


class Player():

    def __init__(self, websocket, color):
        self.websocket = websocket
        self.color = color


class Game():

    def __init__(self, websocket_1, websocket_2):
        self.board = Board()
        self.player_1 = Player(websocket_1, WHITE)
        self.player_2 = Player(websocket_2, BLACK)

    def handle_move(self, start_field, end_field, websocket):

        if self.player_1.websocket == websocket:
            current_player = self.player_1
        elif self.player_2.websocket == websocket:
            current_player = self.player_2
        else:
            raise Exception('You are not a participant of game')

        check = self.board.is_check(on_color=current_player.color)
        piece = self.board[start_field]
        if not piece:
            raise Exception('That is empty field!')
        if piece.color != current_player.color:
            raise Exception('It is not your piece!')
        if end_field not in piece.available_moves(self.board, check=check):
            raise Exception(
                f"Invalid move! Possibilities of this piece: {piece.available_moves(self.board, check=check)}")

        potential_board = self.board.simulate_move(start_field, end_field)
        if potential_board.is_check(on_color=current_player.color):
            raise Exception("Illegal move due to attack on your king")

        if (potential_board.is_check(on_color=opposite_color(current_player.color)) and
                potential_board.is_stalemate(on_color=opposite_color(current_player.color), check=True)):
            self.win_game()

        if potential_board.is_stalemate(on_color=opposite_color(current_player.color)):
            self.draw_game()

        self.board.make_move(start_field, end_field)

    def win_game(self):
        raise Exception('Check-mate!')

    def draw_game(self):
        print("Are ya winning, son?")


if __name__ == "__main__":

    player_1 = Player('player_1', WHITE)
    player_2 = Player('player_2', BLACK)
    game = Game(player_1, player_2)

    # print(game.board['c3'])
    # game.board.print_board()


####################################################
# Szfczyk

    # print('\n')

    game.handle_move('e2', 'e4', player_1)
    # game.board.print_board()
    # print('\n')

    game.handle_move('b7', 'b6', player_2)
    # game.board.print_board()
    # print('\n')

    game.handle_move('d1', 'f3', player_1)
    # game.board.print_board()
    # print('\n')

    game.handle_move('a7', 'a5', player_2)
    # game.board.print_board()
    # print('\n')

    game.handle_move('f1', 'c4', player_1)
    # game.board.print_board()
    # print('\n')

    game.handle_move('b8', 'a6', player_2)

    # game.board.print_board()
    # print('\n')

    game.handle_move('f3', 'f7', player_1)
    game.board.print_board()



    print(game.board.is_check(BLACK))
    king = game.board.king[BLACK]
    print(king.color)
    print(king.position_code)
    quen = game.board['f7']
    print(quen.available_moves(game.board))
    print('\n')



####################################################
# # Mat w dwóch

    # print('\n')
    # game.handle_move((5, 6), (5, 4), player_1)
    # game.board.print_board()

    # print(game.board.king[WHITE].available_moves(game.board))
    # print(game.board.king[BLACK].available_moves(game.board))

    # print('\n')
    # game.handle_move((4, 1), (4, 2), player_2)
    # game.board.print_board()

    # print('\n')
    # game.handle_move((6, 6), (6, 4), player_1)
    # game.board.print_board()

    # print('\n')

    # game.handle_move((3, 0), (7, 4), player_2)
    # game.board.print_board()

    # print(game.board.king[WHITE].available_moves(game.board))


####################################################
# odsłoniecię szacha od przeciwnika

    # print('\n')
    # game.handle_move((2, 6), (2, 4), player_1)
    # game.board.print_board()

    # print('\n')
    # game.handle_move((3, 1), (3, 3), player_2)
    # game.board.print_board()

    # print('\n')
    # game.handle_move((3, 7), (0, 4), player_1)
    # game.board.print_board()

    # print('\n')

    # game.handle_move((2, 1), (2, 3), player_2)
    # game.board.print_board()

#########################################################
# pat test

# class Board ...
    # TEST_BOARD = [
    #     [' ', King(WHITE, (1,0)), ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', Queen(BLACK, (7,1))],
    #     [' ', ' ', ' ', King(BLACK, (3,2)), ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #     [' ', ' ', ' ', ' ', ' ', Bishop(BLACK, (5,5)), ' ', Pawn(BLACK, (7,5))],
    #     [' ', ' ', ' ', ' ', ' ', Pawn(WHITE, (5,6)), ' ', Pawn(WHITE, (7,6))],
    #     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], ]

    # def __init__(self, test=False):
    #     if not test:
    #         self.array = self.STARTING_BOARD
    #         self.all_pieces = {BLACK: set(), WHITE: set()}
    #         self.place_pieces()
    #         self.king = {
    #             BLACK: self.STARTING_BOARD[0][4], WHITE: self.STARTING_BOARD[7][4]}
    #     if test:
    #         self.array = self.TEST_BOARD
    #         self.all_pieces = {BLACK: set(), WHITE: set()}
    #         for row in self.TEST_BOARD:
    #             for piece in row:
    #                 if not EMPTY and piece.color==BLACK:
    #                     self.all_pieces[BLACK].add(piece)
    #                 if not EMPTY and piece.color==WHITE:
    #                     self.all_pieces[WHITE].add(piece)
    #         self.king = {
    #             BLACK: self.TEST_BOARD[2][3], WHITE: self.TEST_BOARD[0][1]}

# class Game():

#     def __init__(self, websocket_1, websocket_2, test=False):
#         self.board = Board()
#         if test:
#             self.board = Board(test=True)

    # game = Game(player_1, player_2, test=True)
    # game.board.print_board()

    # print('\n')
    # game.handle_move((7, 1), (3, 1), player_2)
    # game.board.print_board()
