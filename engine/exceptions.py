class ChessEngineException(Exception):
    """Базовый класс для ошибок шахматного движка."""
    pass

class InvalidMoveError(ChessEngineException):
    """Вызывается при попытке сделать некорректный ход."""
    pass