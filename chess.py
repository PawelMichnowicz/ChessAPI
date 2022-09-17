WHITE = 'white'
BLACK = 'black'

EMPTY = ' '

#


class Piece():

    rock_steps = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    bishop_steps = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
    royal_steps = [*rock_steps, *bishop_steps]
    knight_steps = [[y_step, x_step] for x_step in [-2, -1, +1, +2]
                    for y_step in [-2, -1, +1, +2] if abs(x_step) != abs(y_step)]
    pawn_steps = {BLACK: 1, WHITE: -1}

    def __init__(self, color, position):
        self.color = color
        self.position = position

    def __repr__(self) -> str:
        return f"{self.__class__.__name__[0]}-{self.color[0]}"

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


class Pawn(Piece):

    def available_moves(self, board):
        return [*self.pawn_moves(self.pawn_steps, board), *self.pawn_captures(self.pawn_steps, board)]


class Knight(Piece):

    def available_moves(self, board):
        return self.take_step(self.knight_steps, board)


class Rock(Piece):

    def available_moves(self, board):
        return self.repeat_steps(self.rock_steps, board)


class Bishop(Piece):

    def available_moves(self, board):
        return self.repeat_steps(self.bishop_steps, board)


class Queen(Piece):

    def available_moves(self, board):
        return self.repeat_steps(self.royal_steps, board)


class King(Piece):

    def available_moves(self, board):
        return self.take_step(self.royal_steps, board)


STARTING_BOARD = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

for num in range(8):
    STARTING_BOARD[6][num] = Pawn(WHITE, (num, 6))
    STARTING_BOARD[1][num] = Pawn(BLACK, (num, 1))


class Board():
    def __init__(self):
        self.array = STARTING_BOARD

    def print_board(self):
        for line in self.array:
            print(line)

    def get_piece(self, position):
        if self.array[position[1]][position[0]] == EMPTY:
            return None
        return self.array[position[1]][position[0]]

    def is_blank(self, position):
        return self.array[position[1]][position[0]] == EMPTY

    def is_in(self, position):
        return -1 < position[1] < 8 and -1 < position[0] < 8


class Player():

    def __init__(self, websocket, color):
        self.websocket = websocket
        self.color = color


class Game():

    def __init__(self, websocket_1, websocket_2):
        self.board = Board()
        self.player_1 = Player(websocket_1, WHITE)
        self.player_2 = Player(websocket_2, BLACK)
        self.turn = self.player_1

    def make_move(self, start_pos, end_pos, websocket):
        if self.player_1.websocket == websocket:
            current_player = self.player_1
        elif self.player_2.websocket == websocket:
            current_player = self.player_2
        else:
            raise Exception('WTF!')

        piece = self.board.get_piece(start_pos)
        target = self.board.get_piece(end_pos)

        if piece == EMPTY:
            raise Exception('That is empty field!')
        if piece.color != current_player.color:
            raise Exception('It is not your piece!')
        if end_pos not in piece.available_moves(self.board):
            raise Exception("Invalid move!")

        if target != EMPTY:
            target.position = None
        piece.position = (end_pos[0], end_pos[1])
        self.board.array[start_pos[0]][start_pos[1]] = EMPTY
        self.board.array[end_pos[0]][end_pos[1]] = piece

        if self.turn == self.player_1:
            self.turn = self.player_2
        else:
            self.turn = self.player_1

        return True


# stworzyć postać gracza


if __name__ == "__main__":

    player_1 = Player('x', WHITE)
    player_2 = Player('y', BLACK)

    kn = Knight(BLACK, (4, 5))
    STARTING_BOARD[5][4] = kn

    rock = Rock(WHITE, (4, 3))
    STARTING_BOARD[3][4] = rock

    bishop = Bishop(WHITE, (3, 4))
    STARTING_BOARD[4][3] = bishop

    queen = Queen(WHITE, (0, 0))
    STARTING_BOARD[0][0] = queen

    king = King(BLACK, (7, 7))
    STARTING_BOARD[7][7] = king

    pawn = Pawn(WHITE, (5, 6))
    STARTING_BOARD[6][5] = pawn

    pawn2 = Pawn(BLACK, (4, 1))
    STARTING_BOARD[1][4] = pawn2

    game = Game(player_1, player_2)
    game.board.print_board()

    print(pawn.available_moves(game.board))

    # print(kn.position)
    # print(kn.available_moves(game.board))

    # print('\n')
    # game.make_move((6,2),(5, 2), player_1)
    # game.board.print_board()
    # print('\n')
    # game.make_move((1,1),(2,1), player_2)
    # game.board.print_board()
    # print('\n')
    # game.make_move((5,2),(4, 2), player_1)
    # game.board.print_board()
    # print('\n')
