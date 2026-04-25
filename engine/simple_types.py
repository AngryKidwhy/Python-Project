
from dataclasses import dataclass
from zmq import Enum


class Color(Enum):
    White = 0
    Black = 1

    def opponents(self) -> 'Color':
        return Color.White if self == Color.Black else Color.Black


@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def is_on_board(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8

