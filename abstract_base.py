from game_orm import GameORM
from player_orm import PlayerORM


class AbstractBase:
    def get_player_info(self, player_id: str) -> PlayerORM:
        raise NotImplementedError

    def set_player_info(self, player: PlayerORM) -> None:
        raise NotImplementedError

    def clear_player(self, player_id: str) -> None:
        raise NotImplementedError

    def get_game_info(self, game_id: str) -> GameORM:
        raise NotImplementedError

    def set_game_info(self, game: GameORM) -> None:
        raise NotImplementedError

    def clear_game(self, game_id: str) -> None:
        raise NotImplementedError

    def create_tables(self) -> None:
        raise NotImplementedError
