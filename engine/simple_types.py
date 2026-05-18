from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Color(Enum):
    WHITE = 0
    BLACK = 1

    def opponent(self) -> 'Color':
        return Color.WHITE if self == Color.BLACK else Color.BLACK


@dataclass(frozen=True)
class Position:
    """Представляет координаты клетки на шахматной доске."""
    row: int
    col: int

    def is_on_board(self) -> bool:
        """Проверяет, находятся ли координаты в пределах доски 8x8."""
        return 0 <= self.row < 8 and 0 <= self.col < 8

    @staticmethod
    def is_valid_notation(notation: str) -> bool:
        if len(notation) != 2:
            return False
        return notation[0] in "abcdefgh" and notation[1] in "12345678"

    @classmethod
    def from_notation(cls, notation: str) -> 'Position':
        if not cls.is_valid_notation(notation):
            raise ValueError("Неверный формат нотации")
        col = ord(notation[0]) - ord('a')
        row = 8 - int(notation[1])
        return cls(row, col)


@dataclass(frozen=True)
class Move:
    """Представляет шахматный ход."""
    start: Position
    end: Position
    piece_moved: 'Piece'
    piece_captured: Optional['Piece'] = None
    is_en_passant: bool = False
    is_castle: bool = False
    is_promotion: bool = False
    promotion_choice: str = 'Q'
    piece_had_moved: bool = False
    rook_had_moved: bool = False

    @property
    def notation(self) -> str:
        """Возвращает строковое представление хода в шахматной нотации."""
        if self.is_castle:
            return "O-O" if self.end.col > self.start.col else "O-O-O"

        cols = "abcdefgh"
        rows = "87654321"
        start_sq = f"{cols[self.start.col]}{rows[self.start.row]}"
        end_sq = f"{cols[self.end.col]}{rows[self.end.row]}"
        
        piece_char = self.piece_moved.char if self.piece_moved.char != 'P' else ""
        capture_mark = "x" if self.piece_captured or self.is_en_passant else ""
        
        if self.piece_moved.char == 'P' and capture_mark:
            piece_char = cols[self.start.col]

        base_notation = f"{piece_char}{capture_mark}{end_sq}"

        if self.is_promotion:
            return f"{base_notation}={self.promotion_choice}"
            
        return base_notation