import os
import boto3
import logging

from exceptions import PlayerDoesntExistInDB, GameDoesntExistInDB
from sequence import Sequence
from game_orm import GameORM
from player_orm import PlayerORM, PlayerState


dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.environ.get('USER_STORAGE_URL'),
    region_name='ru-central1',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)


def create_database():
    dynamodb.create_table(
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

    dynamodb.create_table(
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


def get_player_info(player_id: str) -> PlayerORM:
    logger = logging.getLogger('hanabigame.database.get_player_info')
    logger.info('start with player_id = ' + str(player_id))
    table_players = dynamodb.Table('players')
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


def get_game_info(game_id: str) -> GameORM:
    table_games = dynamodb.Table('games')
    response = table_games.get_item(Key={'id': game_id})

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


def finish_game_for_player(player_id):
    table_players = dynamodb.Table('players')
    table_players.delete_item(Key={'id': player_id})


def finish_game(game_id):
    table_games = dynamodb.Table('games')
    table_games.delete_item(Key={'id': game_id})


def create_game(game_id, player, name):
    table_games = dynamodb.Table('games')
    table_games.put_item(
        Item={
            'id': str(game_id),
            'state': 1,
            'player1': player,
        }
    )
    table_players = dynamodb.Table('players')
    table_players.put_item(
        Item={
            'id': player,
            'name': name,
            'state': 3,
            'game_id': str(game_id),
        }
    )


def set_game_info(game: GameORM) -> None:
    table_games = dynamodb.Table('games')
    table_games.put_item(
        Item={
            'id': game.id,
            'state': game.state,
            'stack': game.stack,
            'table': game.table,
            'trash': game.trash,
            'hints': game.hints,
            'lives': game.lives,
            'player_ids': game.player_ids,
        }
    )


def set_player_info(player: PlayerORM) -> None:
    logger = logging.getLogger('hanabigame.database.set_player_info')
    logger.info('start')
    table_players = dynamodb.Table('players')
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
