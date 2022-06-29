from abc import ABC, abstractmethod
from game_orm import GameORM
from player_orm import PlayerORM


class AbstractBase(ABC):
    @abstractmethod
    def get_player_info(self, player_id: str) -> PlayerORM:
        pass

    @abstractmethod
    def set_player_info(self, player: PlayerORM) -> None:
        pass

    @abstractmethod
    def clear_player(self, player_id: str) -> None:
        pass

    @abstractmethod
    def get_game_info(self, game_id: str) -> GameORM:
        pass

    @abstractmethod
    def set_game_info(self, game: GameORM) -> None:
        pass

    @abstractmethod
    def clear_game(self, game_id: str) -> None:
        pass

    @abstractmethod
    def create_tables(self) -> None:
        pass


class GameDoesntExistInDB(Exception):
    pass


class PlayerDoesntExistInDB(Exception):
    pass
