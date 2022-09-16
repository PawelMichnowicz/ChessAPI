WHITE = 'white'
BLACK = 'black'

EMPTY = ' '

class Piece():

    def __init__(self, color, position):
        self.color = color
        self.position = position

    def __repr__(self) -> str:
        return f"{self.__class__.__name__[0]}-{self.color[0]}"


class Pawn(Piece):

    def available_moves(self, board):
        y,x = self.position
        list_moves = []

        if self.color == BLACK:
            if board.is_blank((y+1, x)):
                list_moves.append((y+1, x))
                if y==1 and board.is_blank((y+2, x)):
                    list_moves.append((y+2, x))

            if x>0 and not board.is_blank((y+1, x-1)) and board.get_piece((y+1, x-1)).color==WHITE:
                list_moves.append((y+1, x-1))
            if x<7 and not board.is_blank((y+1, x+1)) and board.get_piece((y+1, x+1)).color==WHITE:
                list_moves.append((y+1, x+1))

        if self.color == WHITE:
            if board.is_blank((y-1, x)):
                list_moves.append((y-1, x))
                if y==6 and board.is_blank((y-2, x)):
                    list_moves.append((y-2, x))

            if x>0 and not board.is_blank((y-1, x-1)) and board.get_piece((y-1, x-1)).color==BLACK:
                list_moves.append((y-1, x-1))
            if x<7 and not board.is_blank((y-1, x+1)) and board.get_piece((y-1, x+1)).color==BLACK:
                list_moves.append((y-1, x+1))

        return (list_moves)




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
    STARTING_BOARD[6][num] = Pawn(WHITE, (6,num))
    STARTING_BOARD[1][num] = Pawn(BLACK, (1,num))


class Board():
    def __init__(self):
        self.array = STARTING_BOARD

    def print_board(self):
        for line in self.array:
            print(line)

    def get_piece(self, position):
        return self.array[position[0]][position[1]]

    def is_blank(self, position):
        return self.array[position[0]][position[1]]==EMPTY


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
        # if self.turn.websocket != websocket:
        #     raise Exception("It is not your turn!")
        if self.player_1.websocket==websocket:
            current_player = self.player_1
        elif self.player_2.websocket==websocket:
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
        piece.position = (end_pos[0],end_pos[1])
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
    game = Game(player_1, player_2)
    game.board.print_board()
    print('\n')
    game.make_move((6,2),(5, 2), player_1)
    game.board.print_board()
    print('\n')
    game.make_move((1,1),(2,1), player_2)
    game.board.print_board()
    print('\n')
    game.make_move((5,2),(4, 2), player_1)
    game.board.print_board()
    print('\n')

