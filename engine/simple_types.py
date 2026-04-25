
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
    row: int
    col: int

    def is_on_board(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8


@dataclass(frozen=True)
class Move:
    start: Position
    end: Position
    piece_moved: 'Piece'
    piece_captured: Optional['Piece'] = None
