import os
import boto3
import logging

from exceptions import PlayerDoesntExistInDB, GameDoesntExistInDB
from sequence import Sequence
from game_orm import GameORM
from player_orm import PlayerORM, PlayerState
from abstract_base import AbstractBase


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
        logger.info('start with player_id = ' + player_id)
        table_players = self.dynamodb.Table('players')
        logger.info('get table players')
        response = table_players.get_item(Key={'id': player_id})
        logger.info('get response')

        if 'Item' not in response:
            raise PlayerDoesntExistInDB

        return PlayerORM(
            id=player_id,
            name=response['Item'].get('name', None),
            state=response['Item'].get('state', PlayerState.NOT_PLAYING),
            game_id=response['Item'].get('game_id', None),
            hand=response['Item'].get('hand', Sequence()),
        )

    def set_player_info(self, player: PlayerORM) -> None:
        logger = logging.getLogger('hanabigame.database.set_player_info')
        logger.info('start')
        table_players = self.dynamodb.Table('players')
        logger.info('get table players')
        item = {
            'id': player.id,
            'name': player.name,
            'state': int(player.state),
            'game_id': player.game_id,
            'hand': str(player.hand),
        }
        logger.info('set item = ' + str(item))
        table_players.put_item(Item=item)
        logger.info('player put')

    def clear_player(self, player_id: str) -> None:
        logger = logging.getLogger('hanabigame.database.clear_player')
        logger.info('start with player_id = ' + player_id)
        table_players = self.dynamodb.Table('players')
        logger.info('get table players')
        table_players.delete_item(Key={'id': player_id})
        logger.info('delete row with player')

    def get_game_info(self, game_id: str) -> GameORM:
        logger = logging.getLogger('hanabigame.database.get_game_info')
        logger.info('start with game_id = ' + game_id)
        table_games = self.dynamodb.Table('games')
        logger.info('get table games')
        response = table_games.get_item(Key={'id': game_id})
        logger.info('get response')

        if 'Item' not in response:
            raise GameDoesntExistInDB

        return GameORM(
            id=game_id,
            state=response['Item']['state'],
            stack=response['Item'].get('stack', Sequence()),
            table=response['Item'].get('table', Sequence()),
            trash=response['Item'].get('trash', Sequence()),
            hints=response['Item'].get('hints', 0),
            lives=response['Item'].get('lives', 0),
            player_ids=response['Item'].get('player_ids', []),
        )

    def set_game_info(self, game: GameORM) -> None:
        logger = logging.getLogger('hanabigame.database.set_game_info')
        logger.info('start')
        table_games = self.dynamodb.Table('games')
        logger.info('get table games')
        item = {
            'id': game.id,
            'state': game.state,
            'stack': game.stack,
            'table': game.table,
            'trash': game.trash,
            'hints': game.hints,
            'lives': game.lives,
            'player_ids': game.player_ids,
        }
        logger.info('set item = ' + str(item))
        table_games.put_item(Item=item)
        logger.info('game put')

    def clear_game(self, game_id: str) -> None:
        logger = logging.getLogger('hanabigame.database.clear_game')
        logger.info('start with game_id = ' + game_id)
        table_games = self.dynamodb.Table('games')
        logger.info('get table games')
        table_games.delete_item(Key={'id': game_id})
        logger.info('delete row with game')

    def create_tables(self) -> None:
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


# def create_game(game_id, player, name):
#     table_games = dynamodb.Table('games')
#     table_games.put_item(
#         Item={
#             'id': str(game_id),
#             'state': 1,
#             'player1': player,
#         }
#     )
#     table_players = dynamodb.Table('players')
#     table_players.put_item(
#         Item={
#             'id': player,
#             'name': name,
#             'state': 3,
#             'game_id': str(game_id),
#         }
#     )
