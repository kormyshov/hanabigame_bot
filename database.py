import os
import boto3
import logging
from pickle import dumps, loads

from game_orm import GameORM
from player_orm import PlayerORM, PlayerState
from abstract_base import AbstractBase, PlayerDoesntExistInDB, GameDoesntExistInDB


class Database(AbstractBase):
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('USER_STORAGE_URL'),
            region_name='ru-central1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )

    def get_player_info(self, player_id: str) -> PlayerORM:
        logger = logging.getLogger('hanabigame.database.get_player_info')
        logger.info('player_id = %s', player_id)
        table_players = self.dynamodb.Table('players')
        response = table_players.get_item(Key={'id': player_id})

        if 'Item' not in response:
            logger.info('player doesnt exist in db')
            raise PlayerDoesntExistInDB

        orm = PlayerORM(
            id=player_id,
            name=response['Item'].get('name', None),
            state=response['Item'].get('state', PlayerState.NOT_PLAYING),
            game_id=response['Item'].get('game_id', None),
            hand=loads(bytes(response['Item'].get('hand'))),
        )
        logger.info('return %s', str(orm))
        return orm

    def set_player_info(self, player: PlayerORM) -> None:
        logger = logging.getLogger('hanabigame.database.set_player_info')
        logger.info('player = %s', str(player))
        table_players = self.dynamodb.Table('players')
        item = {
            'id': player.id,
            'name': player.name,
            'state': int(player.state),
            'game_id': player.game_id,
            'hand': dumps(player.hand),
        }
        table_players.put_item(Item=item)
        logger.info('end')

    def clear_player(self, player_id: str) -> None:
        logger = logging.getLogger('hanabigame.database.clear_player')
        logger.info('player_id = %s', player_id)
        table_players = self.dynamodb.Table('players')
        table_players.delete_item(Key={'id': player_id})
        logger.info('end')

    def get_game_info(self, game_id: str) -> GameORM:
        logger = logging.getLogger('hanabigame.database.get_game_info')
        logger.info('game_id = %s', game_id)
        table_games = self.dynamodb.Table('games')
        response = table_games.get_item(Key={'id': game_id})

        if 'Item' not in response:
            logger.info('game does not exist in db')
            raise GameDoesntExistInDB

        orm = GameORM(
            id=game_id,
            state=response['Item']['state'],
            stack=loads(bytes(response['Item'].get('stack'))),
            table=loads(bytes(response['Item'].get('table'))),
            trash=loads(bytes(response['Item'].get('trash'))),
            hints=response['Item'].get('hints', 0),
            lives=response['Item'].get('lives', 0),
            player_ids=list(response['Item'].get('player_ids', '').split()),
        )
        logger.info('return %s', str(orm))
        return orm

    def set_game_info(self, game: GameORM) -> None:
        logger = logging.getLogger('hanabigame.database.set_game_info')
        logger.info('game = %s', str(game))
        table_games = self.dynamodb.Table('games')
        item = {
            'id': game.id,
            'state': int(game.state),
            'stack': dumps(game.stack),
            'table': dumps(game.table),
            'trash': dumps(game.trash),
            'hints': int(game.hints),
            'lives': int(game.lives),
            'player_ids': ' '.join(game.player_ids),
        }
        table_games.put_item(Item=item)
        logger.info('end')

    def clear_game(self, game_id: str) -> None:
        logger = logging.getLogger('hanabigame.database.clear_game')
        logger.info('game_id = %s', game_id)
        table_games = self.dynamodb.Table('games')
        table_games.delete_item(Key={'id': game_id})
        logger.info('end')

    def create_tables(self) -> None:
        logger = logging.getLogger('hanabigame.database.create_tables')
        logger.info('start')
        self.dynamodb.create_table(
            TableName='players',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH',
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N',
                },
            ],
        )

        self.dynamodb.create_table(
            TableName='games',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH',
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N',
                },
            ],
        )
        logger.info('end')
