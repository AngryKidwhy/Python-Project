class ChessEngineException(Exception):
    """Базовый класс для ошибок шахматного движка."""
    pass

class InvalidMoveError(ChessEngineException):
    """Вызывается при попытке сделать некорректный ход."""
    pass

class InvalidTurnError(ChessEngineException):
    """Вызывается при попытке сделать ход фигурой не своего цвета."""
    pass

class ResourceLoadError(ChessEngineException):
    """Вызывается при ошибке загрузки графических ресурсов."""
    pass