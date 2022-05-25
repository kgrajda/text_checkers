class WrongPositionException(Exception):
    def __init__(self, place):
        self.place = place

    def __str__(self):
        return f"{ f'[{self.place}] ' if self.place is not None else ''}Incorrect position coordinates."


class WrongMoveException(Exception):
    def __init__(self, place):
        self.move = place

    def __str__(self):
        return f"[{self.move}] Incorrect move."


class WrongMoveSyntax(WrongMoveException):
    def __str__(self):
        return (
            f"[{self.move}] Incorrect move syntax. Example of a correct move: b1 -> c2"
        )


class EmptyCellException(WrongMoveException):
    def __str__(self):
        return f"[{self.move}] Cell is empty."


class CellNotEmptyException(WrongMoveException):
    def __str__(self):
        return f"[{self.move}] Cell is not empty."


class ImpossibleMoveException(WrongMoveException):
    def __str__(self):
        return f"[{self.move}] Impossible move."


class NotYourCellException(WrongMoveException):
    def __str__(self):
        return f"[{self.move}] Cell contains enemy's piece."
