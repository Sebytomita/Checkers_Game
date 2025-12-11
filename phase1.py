import pygame
import sys

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
DARK_SQUARE = (0, 0, 0)
LIGHT_SQUARE = (238, 238, 210)
RED = (220, 20, 60)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)

class Piece:
    PADDING = 15
    OUTLINE = 2
    
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.x = 0
        self.y = 0
        self.calc_pos()
    
    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    
    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GRAY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
    
    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()


class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.black_left = 12
        self.create_board()
    
    def draw_squares(self, win):
        win.fill(DARK_SQUARE)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, LIGHT_SQUARE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, GRAY))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
    
    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)
    #ASCII DEBUG
    def print_ascii(self):
        print("\n  0 1 2 3 4 5 6 7", flush=True)
        print("  ----------------", flush=True)
        for row in range(ROWS):
            print(f"{row}|", end="", flush=True)
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    if piece.color == RED:
                        print("R" , end=" ", flush=True)
                    else:
                        print("b" , end=" ", flush=True)
                elif (row + col) % 2 == 1:
                    print(".", end=" ", flush=True)  
                else:
                    print(" ", end=" ", flush=True)  
            print(f"|{row}", flush=True)
        print("  ----------------", flush=True)
        print("  0 1 2 3 4 5 6 7", flush=True)
        print("\nLegend: R=Red, b=Black(Gray), .=Empty dark square\n", flush=True)
    
    def get_piece(self, row, col):
        return self.board[row][col]
    
    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
    
    def get_valid_moves(self, piece):
        
        moves = {}
        row = piece.row
        col = piece.col
        
        directions = []
        if piece.color == RED:
            # Red moves up (negative row direction)
            directions.extend([(-1, -1), (-1, 1)])
        if piece.color == GRAY:
            # Gray moves down (positive row direction)
            directions.extend([(1, -1), (1, 1)])
        
        # Check each diagonal direction (only one square)
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            
            # Check if position is valid and empty
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if self.board[new_row][new_col] == 0:
                    moves[(new_row, new_col)] = []  
        
        return moves

class Game:
    def __init__(self, win):
        self._init()
        self.win = win
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()
    
    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
    
    def reset(self):
        self._init()
    
    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        
        return False
    
    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            self.change_turn()
        else:
            return False
        
        return True
    
    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)
    
    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = GRAY
        else:
            self.turn = RED
        
        print(f"\n{'='*40}", flush=True)
        print(f"Turn: {'RED' if self.turn == RED else 'GRAY'}", flush=True)
        self.board.print_ascii()


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def main():
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Checkers - Phase 1')
    
    clock = pygame.time.Clock()
    game = Game(WIN)
    
    # Print initial board state
    print("\n" + "="*40)
    print("CHECKERS - PHASE 1")
    print("="*40)
    print("Initial Board:")
    game.board.print_ascii()
    
    run = True
    while run:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)
        
        game.update()
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()