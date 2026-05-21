from engine.board import Board
from engine.simple_types import Position, Color
from engine.pieces import Pawn, King, Rook

def test_pawn_initial_double_step():
    """Проверяет, что пешка может сделать двойной шаг только если она еще не ходила."""
    board = Board()
    white_pawn = board.get_piece_at(Position.from_notation("e2"))
    moves = white_pawn.get_valid_moves(board)
    
    end_positions = [move.end for move in moves]
    assert Position.from_notation("e3") in end_positions
    assert Position.from_notation("e4") in end_positions

    white_pawn.has_moved = True
    moves_after = white_pawn.get_valid_moves(board)
    end_positions_after = [move.end for move in moves_after]
    
    assert Position.from_notation("e3") in end_positions_after
    assert Position.from_notation("e4") not in end_positions_after

def test_castling_pseudo_legal_moves():
    """Проверяет псевдолегальную генерацию рокировки при пустых полях."""
    board = Board()
    board._grid = [[None for _ in range(8)] for _ in range(8)]
    
    king = King(Color.WHITE, Position.from_notation("e1"))
    rook_kingside = Rook(Color.WHITE, Position.from_notation("h1"))
    
    board._set_piece(king)
    board._set_piece(rook_kingside)
    
    moves = king.get_valid_moves(board)
    castling_moves = [m for m in moves if m.is_castle]
    
    assert len(castling_moves) == 1
    assert castling_moves[0].end == Position.from_notation("g1")
