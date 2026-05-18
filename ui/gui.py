import pygame
import os
from typing import Optional, Tuple
from engine.board import Board
from engine.simple_types import Position, Color
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

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._handle_click(pygame.mouse.get_pos())
            
            self._draw_state()
            self.clock.tick(MAX_FPS)
            pygame.display.flip()

    def _handle_click(self, mouse_pos: Tuple[int, int]):
        """
        Обрабатывает клик мыши, выделяет фигуры и инициирует выполнение хода.

        Args:
            mouse_pos: Кортеж с координатами клика (x, y) в пикселях.
        """
        col = mouse_pos[0] // SQ_SIZE
        row = mouse_pos[1] // SQ_SIZE
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
                self.valid_moves = piece_at_click.get_valid_moves(self.board)
            else:
                self.selected_sq = None
                self.player_clicks = []
                self.valid_moves = []
        else:
            self.player_clicks.append(clicked_pos)
            start_pos, end_pos = self.player_clicks
            
            move_to_make = next((m for m in self.valid_moves if m.end == end_pos), None)
            
            if move_to_make:
                self.board.execute_move(move_to_make)
                self.board.change_turn()
            
            self.selected_sq = None
            self.player_clicks = []
            self.valid_moves = []

    def _draw_state(self):
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()

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