import copy

WHITE = 'white'
BLACK = 'black'

EMPTY = ' '

# szach z odsłony - done
# pat i szach-mat - done
# promocja pionka
# Obsługa notyfikacji szachowej
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


class Piece():

    rook_steps = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    bishop_steps = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
    royal_steps = [*rook_steps, *bishop_steps]
    knight_steps = [[y_step, x_step] for x_step in [-2, -1, +1, +2]
                    for y_step in [-2, -1, +1, +2] if abs(x_step) != abs(y_step)]
    pawn_steps = {BLACK: 1, WHITE: -1}

    def __init__(self, color, position):
        self.color = color
        self.position = position

    def __repr__(self) -> str:
        return f"{self.__class__.__name__[0]}-{self.color[0]}"

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {self.position}'

    def repeat_steps(self, steps, board):
        x, y = self.position
        list_moves = []
        for step in steps:
            range = 1
            while True:
                new_position = (x+range*step[1], y+range*step[0])
                if board.is_in(new_position) and board.is_blank(new_position):
                    list_moves.append(new_position)
                    range += 1
                elif board.is_in(new_position) and board.get_piece(new_position).color != self.color:
                    list_moves.append(new_position)
                    break
                else:
                    break
        return list_moves

    def take_step(self, steps, board):
        x, y = self.position
        list_moves = []
        for step in steps:
            new_position = (x+step[1], y+step[0])
            if board.is_in(new_position) and (board.is_blank(new_position) or board.get_piece(new_position).color != self.color):
                list_moves.append(new_position)
        return list_moves


    def pawn_moves(self, steps, board):
        x, y = self.position
        list_moves = []
        new_position = (x, y+steps[self.color])
        if board.is_in(new_position) and board.is_blank(new_position):
            list_moves.append(new_position)
            if ((self.color == BLACK and y == 1) or (self.color == WHITE and y == 6)) and board.is_blank((x, y+2*steps[self.color])):
                list_moves.append((x, y+2*steps[self.color]))
        return list_moves

    def pawn_captures(self, steps, board):
        x, y = self.position
        list_moves = []
        for new_position in [(x-1, y+steps[self.color]), (x+1, y+steps[self.color])]:
            if board.is_in(new_position) and not board.is_blank(new_position) and board.get_piece(new_position).color != self.color:
                list_moves.append(new_position)
        return list_moves

    def legal_moves_if_check(self, possible_moves, board):
        legal_moves = []
        for move in possible_moves:
            potential_board = board.simulate_move(self.position, move)
            if not potential_board.is_check(on_color=self.color):
                legal_moves.append(move)
            return legal_moves


class Pawn(Piece):

    def available_moves(self, board, check=False):
        possible_moves = [
            *self.pawn_moves(self.pawn_steps, board), *self.pawn_captures(self.pawn_steps, board)]
        if not check:
            return possible_moves
        return self.legal_moves_if_check(possible_moves, board)


class Knight(Piece):

    def __repr__(self):
        return f'N-{self.color}'

    def available_moves(self, board, check=False):
        possible_moves = self.take_step(self.knight_steps, board)
        if not check:
            return possible_moves
        return self.legal_moves_if_check(possible_moves, board)


class Rook(Piece):

    def available_moves(self, board, check=False):
        possible_moves = self.repeat_steps(self.rook_steps, board)
        if not check:
            return possible_moves
        return self.legal_moves_if_check(possible_moves, board)


class Bishop(Piece):

    def available_moves(self, board, check=False):
        possible_moves = self.repeat_steps(self.bishop_steps, board)
        if not check:
            return possible_moves
        return self.legal_moves_if_check(possible_moves, board)


class Queen(Piece):

    def available_moves(self, board, check=False):
        possible_moves = self.repeat_steps(self.royal_steps, board)
        if not check:
            return possible_moves
        return self.legal_moves_if_check(possible_moves, board)


class King(Piece):

    def possible_moves(self, board):
        return self.take_step(self.royal_steps, board)

    def available_moves(self, board, check=False):
        legal_moves = self.possible_moves(board)
        for move in self.possible_moves(board):
            potential_board = board.simulate_move(self.position, move)
            attackers = potential_board.all_pieces[opposite_color(self.color)].copy()
            attackers.remove(potential_board.king[opposite_color(self.color)])
            for piece in attackers:
                for target in piece.available_moves(potential_board):
                    if target == move:
                        legal_moves.remove(move)
        return legal_moves


# Board["a"][1]=["A1"]
class Board():

    STARTING_BOARD = [
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], ]

    def __init__(self):

        self.array = self.STARTING_BOARD
        self.all_pieces = {BLACK: set(), WHITE: set()}
        self.place_pieces()
        self.king = {
            BLACK: self.STARTING_BOARD[0][4], WHITE: self.STARTING_BOARD[7][4]}

    def place_pieces(self):
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for num in range(8):
            white_piece = placement[num](WHITE, (num, 7))
            black_piece = placement[num](BLACK, (num, 0))
            white_pawn = Pawn(WHITE, (num, 6))
            black_pawn = Pawn(BLACK, (num, 1))
            self.all_pieces[WHITE].update({white_piece, white_pawn})
            self.all_pieces[BLACK].update({black_piece, black_pawn})
            self.array[6][num] = white_pawn
            self.array[7][num] = white_piece
            self.array[1][num] = black_pawn
            self.array[0][num] = black_piece

    def print_board(self):
        for line in self.array:
            print(line)

    def get_piece(self, position):
        if self.array[position[1]][position[0]] == EMPTY:
            return None
        return self.array[position[1]][position[0]]

    def is_no_legal_move(self, on_color, check=False):
        for piece in self.all_pieces[on_color]:
            if piece.available_moves(self, check):
                return False
        return True

    def is_check(self, on_color):
        king = self.king[on_color]
        attackers = self.all_pieces[opposite_color(on_color)]
        for piece in attackers:
            for target in piece.available_moves(self):
                if target == king.position:
                    return True
        return False

    def is_blank(self, position):
        return self.array[position[1]][position[0]] == EMPTY

    def is_in(self, position):
        return -1 < position[1] < 8 and -1 < position[0] < 8

    def make_move(self, start_pos, end_pos, test_board=None):
        if test_board:
            board = test_board
        else:
            board = self

        piece = board.get_piece(start_pos)
        target = board.get_piece(end_pos)
        if target:
            target.position = None
            board.all_pieces[target.color].discard(target)
        piece.position = (end_pos[0], end_pos[1])
        board.array[start_pos[1]][start_pos[0]] = EMPTY
        board.array[end_pos[1]][end_pos[0]] = piece
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
        piece = self.board.get_piece(start_field)
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
                potential_board.is_no_legal_move(on_color=opposite_color(current_player.color), check=True)):
            self.win_game()

        if potential_board.is_no_legal_move(on_color=opposite_color(current_player.color)):
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

####################################################
# Szfczyk

    print('\n')
    game.handle_move((4, 6), (4, 4), player_1)
    game.board.print_board()

    print('\n')
    game.handle_move((4, 1), (4, 3), player_2)
    game.board.print_board()

    print('\n')
    game.handle_move((3, 7), (5, 5), player_1)
    game.board.print_board()

    print('\n')
    game.handle_move((1, 0), (0, 2), player_2)
    game.board.print_board()

    print('\n')
    game.handle_move((5, 7), (2, 4), player_1)
    game.board.print_board()

    print('\n')
    game.handle_move((1, 1), (1, 2), player_2)
    game.board.print_board()

    print('\n')
    game.handle_move((5, 5), (5, 1), player_1)
    game.board.print_board()

    print(game.board.king[BLACK].available_moves(game.board))

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

## class Board ...
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






