import pytest
from engine.simple_types import Position, Color, Move
from engine.pieces import Pawn

def test_position_is_on_board():
    """Проверяет границы шахматной доски для координат."""
    valid_pos = Position(0, 0)
    assert valid_pos.is_on_board() is True

    invalid_pos_row = Position(8, 0)
    assert invalid_pos_row.is_on_board() is False

    invalid_pos_col = Position(0, -1)
    assert invalid_pos_col.is_on_board() is False

def test_position_from_notation():
    """Проверяет корректность конвертации шахматной нотации в координаты (row, col)."""
    pos_e2 = Position.from_notation("e2")
    assert pos_e2.row == 6
    assert pos_e2.col == 4

    pos_a8 = Position.from_notation("a8")
    assert pos_a8.row == 0
    assert pos_a8.col == 0

def test_position_invalid_notation():
    """Проверяет выброс ошибки при передаче неверной нотации."""
    with pytest.raises(ValueError):
        Position.from_notation("x9")
    with pytest.raises(ValueError):
        Position.from_notation("e22")

def test_move_notation_generation():
    """Проверяет правильность генерации текстовой записи хода для протокола."""
    start = Position.from_notation("e2")
    end = Position.from_notation("e4")
    pawn = Pawn(Color.WHITE, start)
    
    normal_move = Move(start, end, pawn)
    assert normal_move.notation == "e4"

    capture_move = Move(start, end, pawn, piece_captured=Pawn(Color.BLACK, end))
    assert capture_move.notation == "exe4"

    castle_move = Move(Position.from_notation("e1"), Position.from_notation("g1"), pawn, is_castle=True)
    assert castle_move.notation == "O-O"

    promo_move = Move(Position.from_notation("e7"), Position.from_notation("e8"), pawn, is_promotion=True, promotion_choice='Q')
    assert promo_move.notation == "e8=Q"
