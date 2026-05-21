from engine.board import Board
from engine.simple_types import Position, Color
from engine.pieces import King, Rook, Queen, Bishop

def test_execute_and_undo_move():
    """Проверяет, что отмена хода полностью восстанавливает предыдущее состояние доски."""
    board = Board()
    start_pos = Position.from_notation("e2")
    end_pos = Position.from_notation("e4")
    
    pawn = board.get_piece_at(start_pos)
    moves = pawn.get_valid_moves(board)
    move = next(m for m in moves if m.end == end_pos)
    
    board.execute_move(move)
    assert board.get_piece_at(start_pos) is None
    assert board.get_piece_at(end_pos) == pawn
    assert board.current_turn == Color.BLACK
    
    board.undo_move()
    assert board.get_piece_at(start_pos) == pawn
    assert board.get_piece_at(end_pos) is None
    assert board.current_turn == Color.WHITE

def test_checkmate_detection():
    """Проверяет логику фиксации мата на примере 'Детского мата' (Fool's Mate)."""
    board = Board()
    
    moves_sequence = [
        ("f2", "f3"),
        ("e7", "e5"),
        ("g2", "g4"),
        ("d8", "h4")
    ]
    
    for start_str, end_str in moves_sequence:
        start = Position.from_notation(start_str)
        end = Position.from_notation(end_str)
        piece = board.get_piece_at(start)
        
        valid_moves = piece.get_valid_moves(board)
        move = next(m for m in valid_moves if m.end == end)
        board.execute_move(move)
        
    assert board.is_checkmate is True
    assert board.is_stalemate is False

def test_filter_legal_moves_prevents_moving_into_check():
    """Проверяет фичу фильтрации: связанная фигура не может открыть короля под шах."""
    board = Board()
    board._grid = [[None for _ in range(8)] for _ in range(8)]
    board.current_turn = Color.WHITE
    
    white_king = King(Color.WHITE, Position.from_notation("e1"))
    white_rook = Rook(Color.WHITE, Position.from_notation("d2"))
    black_bishop = Bishop(Color.BLACK, Position.from_notation("a5"))
    
    board._set_piece(white_king)
    board._set_piece(white_rook)
    board._set_piece(black_bishop)
    
    pseudo_moves = white_rook.get_valid_moves(board)
    assert len(pseudo_moves) > 0
    
    legal_moves = board.get_legal_moves(white_rook)
    assert len(legal_moves) == 0