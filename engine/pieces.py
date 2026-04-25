from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from engine.simple_types import Color, Position, Move

if TYPE_CHECKING:
    from engine.board import Board

class Piece(ABC):
    def __init__(self, color: Color, pos: Position):
        self.color = color
        self.pos = pos
        self.has_moved = False
    
    @abstractmethod
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        pass

    def _find_moves(self, board: 'Board', directions: List[tuple[int, int]], slides: int = 8) -> List[Move]:
        valid_moves = []
        for dr, dc in directions:
            for i in range(1, slides + 1):
                to_pos = Position(self.pos.row + dr * i, self.pos.col + dc * i)
                
                if not to_pos.is_on_board():
                    break

                to_piece: Piece = board.get_piece_at(to_pos)
                if to_piece is None:
                    valid_moves.append(Move(self.pos, to_pos, self))
                else:
                    if to_piece.color != self.color:
                        valid_moves.append(Move(self.pos, to_pos, self, to_piece))
                    break
        return valid_moves


class Knight(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
        return self._find_moves(board, directions, 1)

class Rook(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return self._find_moves(board, directions)

class Bishop(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._find_moves(board, directions)

class Queen(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._find_moves(board, directions)

class King(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._find_moves(board, directions, 1)

class Pawn(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Move]:
        moves = []
        dr = -1 if self.color == Color.WHITE else 1

        one_step = Position(self.pos.row + dr, self.pos.col)
        if one_step.is_on_board() and board.get_piece_at(one_step) is None:
            moves.append(Move(self.pos, one_step, self))

            if not self.has_moved:
                two_steps = Position(self.pos.row + 2 * dr, self.pos.col)
                if board.get_piece_at(two_steps) is None:
                    moves.append(Move(self.pos, two_steps, self))

        for dc in [-1, 1]:
            diag_pos = Position(self.pos.row + dr, self.pos.col + dc)
            if diag_pos.is_on_board():
                target_piece = board.get_piece_at(diag_pos)
                if target_piece and target_piece.color != self.color:
                    moves.append(Move(self.pos, diag_pos, self, target_piece))
                    
        return moves
