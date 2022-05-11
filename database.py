import os
import boto3
import logging


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


def get_player_info(player_id):
    logger = logging.getLogger('hanabigame.database.get_player_info')
    logger.info('start')
    table_players = dynamodb.Table('players')
    logger.info('get table')
    response = table_players.get_item(Key={'id': player_id})
    logger.info('get item')
    return response


def get_game_info(game_id):
    table_games = dynamodb.Table('games')
    response = table_games.get_item(Key={'id': game_id})
    return response


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


def set_game_info(game_id, state, stack, table, trash, players, hints, lives):
    table_games = dynamodb.Table('games')
    item = {
        'id': game_id,
        'state': state,
        'stack': stack,
        'table': table,
        'trash': trash,
        'hints': hints,
        'lives': lives,
    }
    item.update(players)
    table_games.put_item(Item=item)


def set_player_info(player_id, player_name, state, game_id, hand):
    table_players = dynamodb.Table('players')
    table_players.put_item(
        Item={
            'id': player_id,
            'name': player_name,
            'state': state,
            'game_id': str(game_id),
            'hand': hand,
        }
    )
