from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Optional
from engine.simple_types import Color, Position, Move

if TYPE_CHECKING:
    from engine.board import Board

class Piece(ABC):
    """Базовый абстрактный класс для всех шахматных фигур."""
    def __init__(self, color: Color, pos: Position):
        self._color = color
        self._pos = pos
        self._has_moved = False

    @property
    def color(self) -> Color:
        return self._color

    @property
    def pos(self) -> Position:
        return self._pos

    @pos.setter
    def pos(self, value: Position):
        self._pos = value

    @property
    def has_moved(self) -> bool:
        return self._has_moved

    @has_moved.setter
    def has_moved(self, value: bool):
        self._has_moved = value

    @property
    @abstractmethod
    def char(self) -> str:
        """Возвращает символьное обозначение фигуры (например, 'N' для коня)."""
        pass
    
    @abstractmethod
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        """Возвращает список всех возможных ходов для фигуры с учетом состояния доски."""
        pass

    def _find_moves(self, board: 'Board', directions: List[tuple[int, int]], slides: int = 8) -> List[Move]:
        valid_moves = []
        for dr, dc in directions:
            for i in range(1, slides + 1):
                to_pos = Position(self.pos.row + dr * i, self.pos.col + dc * i)
                
                if not to_pos.is_on_board():
                    break

                to_piece: Optional[Piece] = board.get_piece_at(to_pos)
                if to_piece is None:
                    valid_moves.append(Move(self.pos, to_pos, self, piece_had_moved=self.has_moved))
                else:
                    if to_piece.color != self.color:
                        valid_moves.append(Move(self.pos, to_pos, self, to_piece, piece_had_moved=self.has_moved))
                    break
        return valid_moves


class Knight(Piece):
    """Класс фигуры 'Конь'. Ходит буквой 'Г', может перепрыгивать фигуры."""
    
    @property
    def char(self) -> str:
        return 'N'

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
        return self._find_moves(board, directions, 1)


class Rook(Piece):
    """Класс фигуры 'Ладья'. Ходит по вертикали и горизонтали."""
    
    @property
    def char(self) -> str:
        return 'R'

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return self._find_moves(board, directions)


class Bishop(Piece):
    """Класс фигуры 'Слон'. Ходит по диагоналям."""
    
    @property
    def char(self) -> str:
        return 'B'

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._find_moves(board, directions)


class Queen(Piece):
    """Класс фигуры 'Ферзь'. Ходит по вертикали, горизонтали и диагоналям."""
    
    @property
    def char(self) -> str:
        return 'Q'

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._find_moves(board, directions)


class King(Piece):
    """Класс фигуры 'Король'. Ходит на одну клетку в любом направлении."""
    
    @property
    def char(self) -> str:
        return 'K'

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        moves = self._find_moves(board, directions, 1)

        if not self.has_moved:
            rook_kingside = board.get_piece_at(Position(self.pos.row, self.pos.col + 3))
            if isinstance(rook_kingside, Rook) and not rook_kingside.has_moved:
                if board.get_piece_at(Position(self.pos.row, self.pos.col + 1)) is None and \
                   board.get_piece_at(Position(self.pos.row, self.pos.col + 2)) is None:
                    moves.append(Move(self.pos, Position(self.pos.row, self.pos.col + 2), self, is_castle=True, piece_had_moved=self.has_moved, rook_had_moved=rook_kingside.has_moved))

            rook_queenside = board.get_piece_at(Position(self.pos.row, self.pos.col - 4))
            if isinstance(rook_queenside, Rook) and not rook_queenside.has_moved:
                if board.get_piece_at(Position(self.pos.row, self.pos.col - 1)) is None and \
                   board.get_piece_at(Position(self.pos.row, self.pos.col - 2)) is None and \
                   board.get_piece_at(Position(self.pos.row, self.pos.col - 3)) is None:
                    moves.append(Move(self.pos, Position(self.pos.row, self.pos.col - 2), self, is_castle=True, piece_had_moved=self.has_moved, rook_had_moved=rook_queenside.has_moved))

        return moves


class Pawn(Piece):
    """Класс фигуры 'Пешка'. Ходит вперед, бьет по диагонали."""
    
    @property
    def char(self) -> str:
        return 'P'

    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        dr = -1 if self.color == Color.WHITE else 1
        promotion_row = 0 if self.color == Color.WHITE else 7

        one_step = Position(self.pos.row + dr, self.pos.col)
        if one_step.is_on_board() and board.get_piece_at(one_step) is None:
            is_promo = one_step.row == promotion_row
            moves.append(Move(self.pos, one_step, self, is_promotion=is_promo, piece_had_moved=self.has_moved))

            if not self.has_moved:
                two_steps = Position(self.pos.row + 2 * dr, self.pos.col)
                if board.get_piece_at(two_steps) is None:
                    moves.append(Move(self.pos, two_steps, self, piece_had_moved=self.has_moved))

        for dc in [-1, 1]:
            diag_pos = Position(self.pos.row + dr, self.pos.col + dc)
            if diag_pos.is_on_board():
                target_piece = board.get_piece_at(diag_pos)
                if target_piece and target_piece.color != self.color:
                    is_promo = diag_pos.row == promotion_row
                    moves.append(Move(self.pos, diag_pos, self, piece_captured=target_piece, is_promotion=is_promo, piece_had_moved=self.has_moved))
                
                elif not target_piece and len(board.move_log) > 0:
                    last_move = board.move_log[-1]
                    if isinstance(last_move.piece_moved, Pawn) and \
                       last_move.end.row == self.pos.row and \
                       last_move.end.col == diag_pos.col and \
                       abs(last_move.start.row - last_move.end.row) == 2:
                        moves.append(Move(self.pos, diag_pos, self, piece_captured=last_move.piece_moved, is_en_passant=True, piece_had_moved=self.has_moved))
                    
        return moves