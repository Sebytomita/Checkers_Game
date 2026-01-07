import pygame
import sys
import copy
import random

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
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Piece:
    PADDING = 15
    OUTLINE = 2
    
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.calc_pos()
    
    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2
    
    def make_king(self):
        self.king = True
    
    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GRAY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            pygame.draw.circle(win, GOLD, (self.x, self.y), radius // 2)
    
    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()


class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.black_left = 12
        self.red_kings = self.black_kings = 0
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
    
    def evaluate(self):
        """Evaluare pentru AI - scor pozitiv = avantaj GRAY"""
        score = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    mult = 1 if piece.color == GRAY else -1
                    score += (15 if piece.king else 10) * mult
                    # Bonus centru
                    if 2 <= row <= 5 and 2 <= col <= 5:
                        score += 2 * mult
                    # Bonus avansare
                    if not piece.king:
                        score += (row if piece.color == GRAY else 7 - row) * 0.5 * mult
        return score
    
    def print_ascii(self):
        print("\n  0 1 2 3 4 5 6 7")
        print("  ----------------")
        for row in range(ROWS):
            print(f"{row}|", end="")
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    if piece.color == RED:
                        print("R" if not piece.king else "K", end=" ")
                    else:
                        print("b" if not piece.king else "k", end=" ")
                elif (row + col) % 2 == 1:
                    print(".", end=" ")
                else:
                    print(" ", end=" ")
            print(f"|{row}")
        print("  ----------------")
        print("  0 1 2 3 4 5 6 7\n")
    
    def get_piece(self, row, col):
        return self.board[row][col]
    
    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        # Promovare la rege
        if (row == ROWS - 1 or row == 0) and not piece.king:
            piece.make_king()
            if piece.color == RED:
                self.red_kings += 1
            else:
                self.black_kings += 1
    
    def get_valid_moves(self, piece):
        captures = self._get_capture_moves(piece)
        if captures:
            return captures
        
        moves = {}
        directions = []
        if piece.color == RED or piece.king:
            directions.extend([(-1, -1), (-1, 1)])
        if piece.color == GRAY or piece.king:
            directions.extend([(1, -1), (1, 1)])
        
        for dr, dc in directions:
            new_row, new_col = piece.row + dr, piece.col + dc
            if 0 <= new_row < ROWS and 0 <= new_col < COLS and self.board[new_row][new_col] == 0:
                moves[(new_row, new_col)] = []
        return moves
    
    def _get_capture_moves(self, piece):
        captures = {}
        directions = []
        if piece.color == RED or piece.king:
            directions.extend([(-1, -1), (-1, 1)])
        if piece.color == GRAY or piece.king:
            directions.extend([(1, -1), (1, 1)])
        
        for dr, dc in directions:
            enemy_row, enemy_col = piece.row + dr, piece.col + dc
            land_row, land_col = piece.row + 2*dr, piece.col + 2*dc
            
            if not (0 <= land_row < ROWS and 0 <= land_col < COLS):
                continue
            
            enemy = self.board[enemy_row][enemy_col] if 0 <= enemy_row < ROWS and 0 <= enemy_col < COLS else 0
            landing = self.board[land_row][land_col]
            
            if enemy != 0 and enemy.color != piece.color and landing == 0:
                captures[(land_row, land_col)] = [enemy]
        return captures
    
    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece.color == RED:
                self.red_left -= 1
            else:
                self.black_left -= 1
    
    def get_all_pieces(self, color):
        return [p for row in self.board for p in row if p != 0 and p.color == color]
    
    def has_captures(self, color):
        return any(self._get_capture_moves(p) for p in self.get_all_pieces(color))
    
    def winner(self):
        if self.red_left <= 0:
            return GRAY
        elif self.black_left <= 0:
            return RED
        return None
    
    def get_all_moves(self, color):
        """Toate mutările pentru AI - capturile sunt obligatorii"""
        moves = []
        has_cap = self.has_captures(color)
        for piece in self.get_all_pieces(color):
            for move, skip in self.get_valid_moves(piece).items():
                if not has_cap or skip:
                    moves.append((piece, move, skip))
        return moves


class AI:
    def __init__(self, difficulty='medium'):
        self.max_depth = {'easy': 1, 'medium': 2, 'hard': 4}.get(difficulty, 2)
        self.difficulty = difficulty
    
    def get_best_move(self, board):
        if self.difficulty == 'easy':
            moves = board.get_all_moves(GRAY)
            return random.choice(moves) if moves else None
        _, best = self.minimax(board, self.max_depth, float('-inf'), float('inf'), True)
        return best
    
    def minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.winner():
            return board.evaluate(), None
        
        color = GRAY if maximizing else RED
        best_move = None
        best_val = float('-inf') if maximizing else float('inf')
        
        for piece, move, skip in board.get_all_moves(color):
            temp = copy.deepcopy(board)
            temp_piece = temp.get_piece(piece.row, piece.col)
            temp.move(temp_piece, move[0], move[1])
            if skip:
                temp.remove(skip)
            
            val = self.minimax(temp, depth - 1, alpha, beta, not maximizing)[0]
            
            if maximizing:
                if val > best_val:
                    best_val, best_move = val, (piece, move, skip)
                alpha = max(alpha, val)
            else:
                if val < best_val:
                    best_val, best_move = val, (piece, move, skip)
                beta = min(beta, val)
            
            if beta <= alpha:
                break
        
        return best_val, best_move


class Menu:
    def __init__(self, win):
        self.win = win
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.state = 'main'
        self.buttons = {
            'vs_ai': pygame.Rect(WIDTH//2 - 150, 250, 300, 60),
            'vs_player': pygame.Rect(WIDTH//2 - 150, 330, 300, 60),
            'easy': pygame.Rect(WIDTH//2 - 150, 250, 300, 60),
            'medium': pygame.Rect(WIDTH//2 - 150, 330, 300, 60),
            'hard': pygame.Rect(WIDTH//2 - 150, 410, 300, 60),
            'back': pygame.Rect(WIDTH//2 - 150, 490, 300, 60)
        }
    
    def draw(self):
        self.win.fill(DARK_SQUARE)
        title = self.font_large.render("CHECKERS", True, WHITE)
        self.win.blit(title, title.get_rect(center=(WIDTH//2, 100)))
        
        mouse = pygame.mouse.get_pos()
        if self.state == 'main':
            self._draw_btn('vs_ai', "Play vs AI", mouse, GREEN)
            self._draw_btn('vs_player', "2 Players", mouse, BLUE)
        else:
            self._draw_btn('easy', "Easy", mouse, GREEN)
            self._draw_btn('medium', "Medium", mouse, GOLD)
            self._draw_btn('hard', "Hard", mouse, RED)
            self._draw_btn('back', "Back", mouse, BLACK)
        pygame.display.update()
    
    def _draw_btn(self, key, text, mouse, color):
        btn = self.buttons[key]
        hover = btn.collidepoint(mouse)
        pygame.draw.rect(self.win, color if hover else GRAY, btn, border_radius=10)
        pygame.draw.rect(self.win, WHITE, btn, 3, border_radius=10)
        txt = self.font_medium.render(text, True, WHITE if hover else color)
        self.win.blit(txt, txt.get_rect(center=btn.center))
    
    def handle_click(self, pos):
        if self.state == 'main':
            if self.buttons['vs_ai'].collidepoint(pos):
                self.state = 'difficulty'
            elif self.buttons['vs_player'].collidepoint(pos):
                return ('player', None)
        else:
            for diff in ['easy', 'medium', 'hard']:
                if self.buttons[diff].collidepoint(pos):
                    return ('ai', diff)
            if self.buttons['back'].collidepoint(pos):
                self.state = 'main'
        return None


class Game:
    def __init__(self, win, ai_mode=False, difficulty='medium'):
        self.win = win
        self.ai_mode = ai_mode
        self.ai = AI(difficulty) if ai_mode else None
        self._init()
    
    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        self.in_capture_sequence = False
        self.moves_without_capture = 0
        self.position_history = []
        self.warning_message = ""
        self.warning_timer = 0
        self.restart_btn = None
        self.menu_btn = None
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves()
        self.draw_info()
        pygame.display.update()
    
    def get_board_state(self):
        return ''.join(
            '.' if p == 0 else ('R' if p.color == RED else 'b') + ('K' if p.king else '')
            for row in self.board.board for p in row
        )
    
    def check_draw(self):
        if self.moves_without_capture >= 20:
            return "20 moves without capture"
        if self.position_history.count(self.get_board_state()) >= 3:
            return "Position repeated 3 times"
        return None
    
    def select(self, row, col):
        if self.selected:
            if self._move(row, col):
                return True
            if not self.in_capture_sequence:
                self.selected = None
                return self.select(row, col)
            else:
                self.warning_message = "You must continue the capture sequence!"
                self.warning_timer = 180
                print("You must continue the capture sequence!")
            return False
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            
            if self.board.has_captures(self.turn):
                captures = self.board._get_capture_moves(piece)
                if not captures:
                    self.selected = None
                    self.valid_moves = {}
                    self.warning_message = "You must capture! Select a piece that can capture."
                    self.warning_timer = 180  # 3 secunde la 60 FPS
                    print("You must capture! Select a piece that can capture.")
                    return False
                self.valid_moves = captures
            return True
        return False
    
    def _move(self, row, col):
        if not self.selected or self.board.get_piece(row, col) != 0 or (row, col) not in self.valid_moves:
            return False
        
        from_pos = (self.selected.row, self.selected.col)
        skipped = self.valid_moves[(row, col)]
        piece_name = 'R' if self.selected.color == RED else 'b'
        
        self.board.move(self.selected, row, col)
        print(f"\nMove: {piece_name} from {from_pos} to ({row}, {col})")
        
        if skipped:
            self.board.remove(skipped)
            self.moves_without_capture = 0
            print(f"  Captured {len(skipped)} piece(s)!")
            more = self.board._get_capture_moves(self.selected)
            if more:
                self.valid_moves = more
                self.in_capture_sequence = True
                print("  Continue capturing! You must complete all available captures.")
                return True
        else:
            self.moves_without_capture += 1
        
        self.selected = None
        self.valid_moves = {}
        self.in_capture_sequence = False
        self.change_turn()
        return True
    
    def ai_move(self):
        if not self.ai or self.turn != GRAY or self.board.winner():
            return
        
        print("\nAI is thinking...")
        best = self.ai.get_best_move(self.board)
        if not best:
            return
        
        piece, move, skip = best
        actual = self.board.get_piece(piece.row, piece.col)
        
        self.selected = actual
        self.update()
        pygame.time.delay(500)
        
        print(f"AI Move: b from ({actual.row}, {actual.col}) to {move}")
        self.board.move(actual, move[0], move[1])
        if skip:
            self.board.remove(skip)
            self.moves_without_capture = 0
            print(f"  AI captured {len(skip)} piece(s)!")
            # Multi-jump
            while True:
                more = self.board._get_capture_moves(actual)
                if not more:
                    break
                self.update()
                pygame.time.delay(400)
                nxt = list(more.keys())[0]
                print(f"AI continues: b from ({actual.row}, {actual.col}) to {nxt}")
                self.board.move(actual, nxt[0], nxt[1])
                self.board.remove(more[nxt])
                print(f"  AI captured {len(more[nxt])} more piece(s)!")
        else:
            self.moves_without_capture += 1
        
        self.selected = None
        self.change_turn()
    
    def draw_valid_moves(self):
        for (r, c), skip in self.valid_moves.items():
            color = GREEN if skip else BLUE
            pygame.draw.circle(self.win, color, (c * SQUARE_SIZE + SQUARE_SIZE//2, r * SQUARE_SIZE + SQUARE_SIZE//2), 15)
        if self.selected:
            r, c = self.selected.row, self.selected.col
            pygame.draw.circle(self.win, (255, 255, 0), (c * SQUARE_SIZE + SQUARE_SIZE//2, r * SQUARE_SIZE + SQUARE_SIZE//2), SQUARE_SIZE//2 - 10, 5)
    
    def draw_info(self):
        font = pygame.font.Font(None, 36)
        small = pygame.font.Font(None, 24)
        
        # Turn
        txt = "Your Turn" if self.turn == RED else ("AI's Turn" if self.ai_mode else "GRAY's Turn")
        self.win.blit(font.render(txt, True, self.turn), (WIDTH - 200, 10))
        
        # Pieces
        self.win.blit(small.render(f"RED: {self.board.red_left} ({self.board.red_kings}K)", True, RED), (10, 10))
        self.win.blit(small.render(f"GRAY: {self.board.black_left} ({self.board.black_kings}K)", True, GRAY), (10, 35))
        self.win.blit(small.render(f"No capture: {self.moves_without_capture}/20", True, WHITE), (10, 60))
        
        # Warning message
        if self.warning_timer > 0:
            self.warning_timer -= 1
            warning_font = pygame.font.Font(None, 42)
            warning_surface = warning_font.render(self.warning_message, True, (255, 100, 100))
            warning_rect = warning_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            # Background pt vizibilitate
            pygame.draw.rect(self.win, (0, 0, 0), warning_rect.inflate(20, 10))
            self.win.blit(warning_surface, warning_rect)
        
        # Draw/Winner
        draw = self.check_draw()
        winner = self.board.winner()
        if draw or winner:
            # Overlay semi-transparent
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.win.blit(overlay, (0, 0))
            
            # Mesaj rezultat
            if draw:
                msg = f"DRAW! ({draw})"
                color = GOLD
            else:
                msg = "YOU WIN!" if winner == RED else ("AI WINS!" if self.ai_mode else "GRAY WINS!")
                color = winner
            
            big_font = pygame.font.Font(None, 72)
            msg_surface = big_font.render(msg, True, color)
            self.win.blit(msg_surface, msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            
            # Buton Restart
            self.restart_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
            mouse = pygame.mouse.get_pos()
            hover = self.restart_btn.collidepoint(mouse)
            pygame.draw.rect(self.win, GREEN if hover else GRAY, self.restart_btn, border_radius=10)
            pygame.draw.rect(self.win, WHITE, self.restart_btn, 3, border_radius=10)
            btn_text = font.render("RESTART", True, WHITE if hover else GREEN)
            self.win.blit(btn_text, btn_text.get_rect(center=self.restart_btn.center))
            
            # Buton Menu
            self.menu_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
            hover_menu = self.menu_btn.collidepoint(mouse)
            pygame.draw.rect(self.win, BLUE if hover_menu else GRAY, self.menu_btn, border_radius=10)
            pygame.draw.rect(self.win, WHITE, self.menu_btn, 3, border_radius=10)
            menu_text = font.render("MENU", True, WHITE if hover_menu else BLUE)
            self.win.blit(menu_text, menu_text.get_rect(center=self.menu_btn.center))
        else:
            self.restart_btn = None
            self.menu_btn = None
    
    def is_game_over(self):
        return self.board.winner() is not None or self.check_draw() is not None
    
    def change_turn(self):
        self.position_history.append(self.get_board_state())
        self.valid_moves = {}
        self.turn = GRAY if self.turn == RED else RED
        
        # ASCII Debug
        print(f"\n{'='*40}")
        print(f"Turn: {'RED (You)' if self.turn == RED else 'GRAY (AI)' if self.ai_mode else 'GRAY'}")
        print(f"Moves without capture: {self.moves_without_capture}/20")
        print(f"RED: {self.board.red_left} pieces ({self.board.red_kings} kings)")
        print(f"GRAY: {self.board.black_left} pieces ({self.board.black_kings} kings)")
        self.board.print_ascii()


def main():
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Checkers - Phase 5')
    
    clock = pygame.time.Clock()
    menu = Menu(WIN)
    game = None
    in_menu = True
    
    print("\n" + "="*40)
    print("CHECKERS - PHASE 5 (Optimized)")
    print("="*40)
    print("Use the menu to select game mode!")
    
    while True:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_menu:
                    result = menu.handle_click(pygame.mouse.get_pos())
                    if result:
                        mode, diff = result
                        game = Game(WIN, ai_mode=(mode == 'ai'), difficulty=diff or 'medium')
                        in_menu = False
                        if mode == 'ai':
                            print(f"\nPlaying against AI on {diff.upper()} difficulty!")
                            print("You are RED, AI is GRAY")
                        else:
                            print("\n2 Player mode selected!")
                        print("\nInitial Board:")
                        game.board.print_ascii()
                elif game:
                    pos = pygame.mouse.get_pos()
                    if game.is_game_over():
                        if game.restart_btn and game.restart_btn.collidepoint(pos):
                            # Restart
                            game._init()
                            print("\n" + "="*40)
                            print("GAME RESTARTED!")
                            print("="*40)
                            print("\nInitial Board:")
                            game.board.print_ascii()
                        elif game.menu_btn and game.menu_btn.collidepoint(pos):
                            in_menu = True
                            menu = Menu(WIN)
                    elif game.turn == RED or not game.ai_mode:
                        r, c = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                        game.select(r, c)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not in_menu:
                in_menu = True
                menu = Menu(WIN)
        
        if in_menu:
            menu.draw()
        elif game:
            if game.ai_mode and game.turn == GRAY and not game.board.winner() and not game.check_draw():
                pygame.time.delay(300)
                game.ai_move()
            game.update()


if __name__ == '__main__':
    main()