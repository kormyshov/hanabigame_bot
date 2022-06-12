from game_orm import GameORM
from player_orm import PlayerORM
from abstract_base import AbstractBase, PlayerDoesntExistInDB, GameDoesntExistInDB


class Dictbase(AbstractBase):
    def __init__(self) -> None:
        self.games = dict()
        self.players = dict()

    def get_player_info(self, player_id: str) -> PlayerORM:
        if player_id not in self.players:
            raise PlayerDoesntExistInDB
        return self.players[player_id]

    def set_player_info(self, player: PlayerORM) -> None:
        self.players[player.id] = player

    def clear_player(self, player_id: str) -> None:
        self.players.pop(player_id)

    def get_game_info(self, game_id: str) -> GameORM:
        if game_id not in self.games:
            raise GameDoesntExistInDB
        return self.games[game_id]

    def set_game_info(self, game: GameORM) -> None:
        self.games[game.id] = game

    def clear_game(self, game_id: str) -> None:
        self.games.pop(game_id)

    def create_tables(self) -> None:
        self.games = dict()
        self.players = dict()
