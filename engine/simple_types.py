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