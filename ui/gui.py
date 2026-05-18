import pygame
import os
import dataclasses
import platform
from typing import Optional, Tuple
from engine.board import Board
from engine.simple_types import Position, Color, Move
from engine.exceptions import ResourceLoadError
from ui.config import WIDTH, HEIGHT, DIMENSION, SQ_SIZE, MAX_FPS, COLOR_LIGHT, COLOR_DARK, COLOR_HIGHLIGHT, COLOR_MOVE_DOT


class ChessGUI:
    """Отвечает за графический интерфейс, отрисовку доски и обработку пользовательского ввода."""
    
    def __init__(self, board: Board):
        self.board = board
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Engine")
        self.clock = pygame.time.Clock()
        self.images = {}
        self.selected_sq: Optional[Position] = None
        self.player_clicks: list[Position] = []
        self.valid_moves = []
        self.promotion_move: Optional[Move] = None
        
        self._load_images()

    def _load_images(self):
        pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
        for piece in pieces:
            path = f"images/{piece}.png"
            if not os.path.exists(path):
                raise ResourceLoadError(f"Файл изображения {path} не найден!")
            try:
                img = pygame.image.load(path).convert_alpha()
                self.images[piece] = pygame.transform.smoothscale(img, (SQ_SIZE, SQ_SIZE))
            except pygame.error as e:
                raise ResourceLoadError(f"Ошибка загрузки {path}: {e}")

    def _get_piece_name(self, piece) -> str:
        color_char = 'w' if piece.color == Color.WHITE else 'b'
        return f"{color_char}{piece.char}"

    def _clear_console(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def _print_protocol(self):
        self._clear_console()
        print("=== ШАХМАТНЫЙ ДВИЖОК ===")
        print("Управление:")
        print("- Мышь: выбор и перемещение фигур")
        print("- Клавиша 'Z': отмена последнего хода (Undo)\n")
        print("=== ПРОТОКОЛ ПАРТИИ ===")
        protocol = self.board.get_game_protocol()
        if protocol:
            print(protocol)
        else:
            print("Партия еще не началась.")
        print("=======================\n")

    def run(self):
        self._print_protocol()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        self._perform_undo()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._handle_click(pygame.mouse.get_pos())
            
            self._draw_state()
            self.clock.tick(MAX_FPS)
            pygame.display.flip()

    def _perform_undo(self):
        """Вызывает логику отката хода и сбрасывает состояния интерфейса."""
        self.board.undo_move()
        self.selected_sq = None
        self.player_clicks = []
        self.valid_moves = []
        self.promotion_move = None
        self._print_protocol()

    def _handle_click(self, mouse_pos: Tuple[int, int]):
        """
        Обрабатывает клик мыши, выделяет фигуры и инициирует выполнение хода.
        Также перехватывает клики для меню превращения пешки.
        """
        if self.board.is_checkmate or self.board.is_stalemate:
            return

        x, y = mouse_pos

        if self.promotion_move:
            menu_rect = pygame.Rect(WIDTH // 2 - 2 * SQ_SIZE, HEIGHT // 2 - SQ_SIZE // 2, 4 * SQ_SIZE, SQ_SIZE)
            if menu_rect.collidepoint(x, y):
                index = (x - menu_rect.x) // SQ_SIZE
                choices = ['Q', 'R', 'B', 'N']
                
                final_move = dataclasses.replace(self.promotion_move, promotion_choice=choices[index])
                self.board.execute_move(final_move)
                self._print_protocol()
            
            self.promotion_move = None
            self.selected_sq = None
            self.player_clicks = []
            self.valid_moves = []
            return

        col = x // SQ_SIZE
        row = y // SQ_SIZE
        clicked_pos = Position(row, col)

        if self.selected_sq == clicked_pos:
            self.selected_sq = None
            self.player_clicks = []
            self.valid_moves = []
            return

        piece_at_click = self.board.get_piece_at(clicked_pos)

        if len(self.player_clicks) == 0 or (piece_at_click and piece_at_click.color == self.board.current_turn):
            if piece_at_click and piece_at_click.color == self.board.current_turn:
                self.selected_sq = clicked_pos
                self.player_clicks = [clicked_pos]
                self.valid_moves = self.board.get_legal_moves(piece_at_click)
            else:
                self.selected_sq = None
                self.player_clicks = []
                self.valid_moves = []
        else:
            self.player_clicks.append(clicked_pos)
            start_pos, end_pos = self.player_clicks
            
            move_to_make = next((m for m in self.valid_moves if m.end == end_pos), None)
            
            if move_to_make:
                if move_to_make.is_promotion:
                    self.promotion_move = move_to_make
                else:
                    self.board.execute_move(move_to_make)
                    self._print_protocol()
                    self.selected_sq = None
                    self.player_clicks = []
                    self.valid_moves = []
            else:
                self.selected_sq = None
                self.player_clicks = []
                self.valid_moves = []

    def _draw_state(self):
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        self._draw_promotion_menu()
        self._draw_game_over()

    def _draw_board(self):
        colors = [COLOR_LIGHT, COLOR_DARK]
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                color = colors[(row + col) % 2]
                rect = pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_highlights(self):
        if self.selected_sq:
            r, c = self.selected_sq.row, self.selected_sq.col
            rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, rect)

        for move in self.valid_moves:
            r, c = move.end.row, move.end.col
            center = (c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2)
            
            if move.piece_captured:
                pygame.draw.circle(self.screen, COLOR_MOVE_DOT, center, SQ_SIZE // 2 - 4, 5)
            else:
                pygame.draw.circle(self.screen, COLOR_MOVE_DOT, center, SQ_SIZE // 6)

    def _draw_pieces(self):
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = self.board.get_piece_at(Position(row, col))
                if piece:
                    piece_name = self._get_piece_name(piece)
                    rect = pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                    self.screen.blit(self.images[piece_name], rect)

    def _draw_promotion_menu(self):
        """Отрисовывает поверх доски меню выбора фигуры для превращения пешки."""
        if self.promotion_move:
            menu_rect = pygame.Rect(WIDTH // 2 - 2 * SQ_SIZE, HEIGHT // 2 - SQ_SIZE // 2, 4 * SQ_SIZE, SQ_SIZE)
            
            pygame.draw.rect(self.screen, pygame.Color("white"), menu_rect)
            pygame.draw.rect(self.screen, pygame.Color("black"), menu_rect, 2)
            
            color_char = 'w' if self.promotion_move.piece_moved.color == Color.WHITE else 'b'
            pieces_to_choose = ['Q', 'R', 'B', 'N']
            
            for i, p_char in enumerate(pieces_to_choose):
                img = self.images[f"{color_char}{p_char}"]
                rect = pygame.Rect(menu_rect.x + i * SQ_SIZE, menu_rect.y, SQ_SIZE, SQ_SIZE)
                self.screen.blit(img, rect)
                if i > 0:
                    pygame.draw.line(self.screen, pygame.Color("black"), (rect.x, rect.y), (rect.x, rect.y + SQ_SIZE), 2)

    def _draw_game_over(self):
        """Отрисовывает экран конца игры при мате или пате."""
        if self.board.is_checkmate or self.board.is_stalemate:
            font = pygame.font.SysFont("Arial", 32, True)
            text = "Мат!" if self.board.is_checkmate else "Пат!"
            surface = font.render(text, True, pygame.Color("black"))
            rect = surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            bg_rect = rect.inflate(20, 20)
            pygame.draw.rect(self.screen, pygame.Color("white"), bg_rect)
            pygame.draw.rect(self.screen, pygame.Color("black"), bg_rect, 2)
            
            self.screen.blit(surface, rect)