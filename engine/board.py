from typing import List, Optional
from engine.simple_types import Color, Position, Move
from engine.pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from engine.exceptions import InvalidMoveError, InvalidTurnError

class Board:
    """Класс шахматной доски, хранящий состояние игры и управляющий перемещением фигур."""
    
    def __init__(self):
        self._grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = Color.WHITE
        self.move_log: List[Move] = []
        self.is_checkmate = False
        self.is_stalemate = False
        self.setup_board()
    
    def setup_board(self):
        """Расставляет фигуры на начальные позиции."""
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
        """
        Устанавливает фигуру на доску в соответствии с ее текущими координатами.
        
        Args:
            piece: Объект фигуры, который необходимо разместить на доске.
        """
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
    
    def execute_move(self, move: Move, is_simulation: bool = False):
        """
        Выполняет ход на доске: обновляет сетку и внутреннее состояние фигуры.
        Также проверяет очередь хода.
        
        Args:
            move: Объект хода, содержащий начальную и конечную позицию.
            is_simulation: Флаг для симуляции хода без проверки конца игры.
        """
        if move.piece_moved is None:
            raise InvalidMoveError("Нет фигуры для выполнения хода")
            
        if move.piece_moved.color != self.current_turn:
            raise InvalidTurnError("Попытка сделать ход фигурой не своего цвета")

        self._grid[move.start.row][move.start.col] = None
        self._grid[move.end.row][move.end.col] = move.piece_moved
        
        move.piece_moved.pos = move.end
        move.piece_moved.has_moved = True

        if move.is_en_passant:
            self._grid[move.start.row][move.end.col] = None

        if move.is_promotion:
            if move.promotion_choice == 'R':
                promoted_piece = Rook(move.piece_moved.color, move.end)
            elif move.promotion_choice == 'B':
                promoted_piece = Bishop(move.piece_moved.color, move.end)
            elif move.promotion_choice == 'N':
                promoted_piece = Knight(move.piece_moved.color, move.end)
            else:
                promoted_piece = Queen(move.piece_moved.color, move.end)
                
            promoted_piece.has_moved = True
            self._grid[move.end.row][move.end.col] = promoted_piece

        if move.is_castle:
            if move.end.col - move.start.col == 2:
                rook = self._grid[move.start.row][7]
                self._grid[move.start.row][7] = None
                self._grid[move.start.row][move.end.col - 1] = rook
                rook.pos = Position(move.start.row, move.end.col - 1)
                rook.has_moved = True
            else:
                rook = self._grid[move.start.row][0]
                self._grid[move.start.row][0] = None
                self._grid[move.start.row][move.end.col + 1] = rook
                rook.pos = Position(move.start.row, move.end.col + 1)
                rook.has_moved = True

        self.move_log.append(move)
        self.change_turn()

        if not is_simulation:
            self._update_game_state()
            
    def undo_move(self):
        """Отменяет последний сделанный ход и восстанавливает состояние игры."""
        if not self.move_log:
            return
            
        move = self.move_log.pop()
        self.change_turn()
        
        self._grid[move.start.row][move.start.col] = move.piece_moved
        self._grid[move.end.row][move.end.col] = move.piece_captured
        
        move.piece_moved.pos = move.start
        move.piece_moved.has_moved = move.piece_had_moved

        if move.piece_captured:
            move.piece_captured.pos = move.end

        if move.is_en_passant:
            self._grid[move.end.row][move.end.col] = None
            self._grid[move.start.row][move.end.col] = move.piece_captured
            move.piece_captured.pos = Position(move.start.row, move.end.col)

        if move.is_promotion:
            self._grid[move.start.row][move.start.col] = move.piece_moved

        if move.is_castle:
            if move.end.col - move.start.col == 2:
                rook = self._grid[move.start.row][move.end.col - 1]
                self._grid[move.start.row][7] = rook
                self._grid[move.start.row][move.end.col - 1] = None
                rook.pos = Position(move.start.row, 7)
                rook.has_moved = move.rook_had_moved
            else:
                rook = self._grid[move.start.row][move.end.col + 1]
                self._grid[move.start.row][0] = rook
                self._grid[move.start.row][move.end.col + 1] = None
                rook.pos = Position(move.start.row, 0)
                rook.has_moved = move.rook_had_moved

        self.is_checkmate = False
        self.is_stalemate = False

    def get_legal_moves(self, piece: Piece) -> List[Move]:
        """Возвращает список ходов, не оставляющих своего короля под атакой."""
        pseudo_moves = piece.get_valid_moves(self)
        legal_moves = []
        for move in pseudo_moves:
            if move.is_castle:
                if self.in_check(piece.color):
                    continue
                d = 1 if move.end.col > move.start.col else -1
                sq1 = Position(move.start.row, move.start.col + d)
                sq2 = Position(move.start.row, move.start.col + 2 * d)
                if self.is_under_attack(sq1, piece.color.opponent()) or self.is_under_attack(sq2, piece.color.opponent()):
                    continue

            self.execute_move(move, is_simulation=True)
            if not self.in_check(piece.color):
                legal_moves.append(move)
            self.undo_move()
            
        return legal_moves

    def in_check(self, color: Color) -> bool:
        """Проверяет, находится ли король заданного цвета под атакой."""
        king_pos = None
        for row in range(8):
            for col in range(8):
                p = self._grid[row][col]
                if isinstance(p, King) and p.color == color:
                    king_pos = p.pos
                    break
            if king_pos:
                break
                
        if not king_pos:
            return False
            
        return self.is_under_attack(king_pos, color.opponent())

    def is_under_attack(self, pos: Position, attacking_color: Color) -> bool:
        """Проверяет, атакуется ли клетка фигурами заданного цвета."""
        for row in range(8):
            for col in range(8):
                p = self._grid[row][col]
                if p and p.color == attacking_color:
                    moves = p.get_valid_moves(self)
                    for move in moves:
                        if move.end == pos:
                            return True
        return False
        
    def change_turn(self):
        """Переключает очередь хода на противоположный цвет."""
        self.current_turn = self.current_turn.opponent()

    def _update_game_state(self):
        """Определяет мат или пат на основе доступных легальных ходов."""
        has_moves = False
        for row in range(8):
            for col in range(8):
                p = self._grid[row][col]
                if p and p.color == self.current_turn:
                    if len(self.get_legal_moves(p)) > 0:
                        has_moves = True
                        break
            if has_moves:
                break
                
        if not has_moves:
            if self.in_check(self.current_turn):
                self.is_checkmate = True
            else:
                self.is_stalemate = True