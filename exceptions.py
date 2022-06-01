class DontExistCard(Exception):
    pass


class CardIsNotInSequence(Exception):
    pass


class GameDoesntExistInDB(Exception):
    pass


class GameDoesntInit(Exception):
    pass


class GameStackIsEmpty(Exception):
    pass


class PlayerDoesntExistInDB(Exception):
    pass


class UnexpectedPlayerState(Exception):
    pass
