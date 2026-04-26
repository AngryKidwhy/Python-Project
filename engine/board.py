from typing import List, Optional
from engine.simple_types import Color, Position, Move
from engine.pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from engine.exceptions import InvalidMoveError

class Board:
    """Класс шахматной доски, хранящий состояние игры и управляющий перемещением фигур."""
    def __init__(self):
        self._grid: List[List[Optional[Piece]]] = [[None for i in range(8)] for i in range(8)]
        self.current_turn = Color.WHITE
        self.setup_board()
    
    def setup_board(self):
        for col in range(8):
            self._set_piece(Pawn(Color.BLACK, Position(1, col)))
            self._set_piece(Pawn(Color.WHITE, Position(6, col)))

        def setup_row(color: Color, row: int):
            pieces_layout = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
            for col, piece_class in enumerate(pieces_layout):
                self._set_piece(piece_class(color, Position(row, col)))

        setup_row(Color.BLACK, 0)
        setup_row(Color.WHITE, 7)
    
    def _set_piece(self, piece: Piece):
        self._grid[piece.pos.row][piece.pos.col] = piece

    def get_piece_at(self, pos: Position) -> Optional[Piece]:
        """
        Возвращает фигуру по заданным координатам.
        
        Args:
            pos: Координаты на доске.
            
        Returns:
            Объект фигуры или None, если клетка пуста/вне доски.
        """
        if not pos.is_on_board():
            return None
        return self._grid[pos.row][pos.col]
    
    def execute_move(self, move: Move):
        """
        Выполняет ход на доске: обновляет сетку и внутреннее состояние фигуры.
        
        Args:
            move: Объект хода, содержащий начальную и конечную позицию.
        """
        if move.piece_moved is None:
            raise InvalidMoveError("Нет фигуры")

        self._grid[move.start.row][move.start.col] = None
        self._grid[move.end.row][move.end.col] = move.piece_moved
        
        move.piece_moved.pos = move.end
        move.piece_moved.has_moved = True
        
    def change_turn(self):
        self.current_turn = self.current_turn.opponent()
