from dictbase import Dictbase
from player import Player
from player_orm import PlayerORM, PlayerState
from sequence import Sequence
from card import Card, CardNumbers, CardColors


def test_start_game():
    db = Dictbase()
    p = Player('1', db)
    seq = Sequence([
        Card(CardNumbers.TWO, CardColors.RAINBOW),
        Card(CardNumbers.FOUR, CardColors.WHITE),
        Card(CardNumbers.FIVE, CardColors.BLUE),
        Card(CardNumbers.THREE, CardColors.GREEN),
    ])
    p.start_game(seq)
    p.save()
    assert db.get_player_info('1') == PlayerORM('1', None, PlayerState.PLAYING, None, seq)


def test_load():
    db = Dictbase()
    p = Player('1', db)
    seq = Sequence([
        Card(CardNumbers.TWO, CardColors.RAINBOW),
        Card(CardNumbers.FOUR, CardColors.WHITE),
        Card(CardNumbers.FIVE, CardColors.BLUE),
        Card(CardNumbers.THREE, CardColors.GREEN),
    ])
    p.start_game(seq)
    p.save()
    p1 = Player('1', db)
    p1.load()
    assert p1.id == p.id
    assert p1.name == p.name
    assert p1.state == p.state
    assert p1.game_id == p.game_id
    assert p1.hand == p.hand


def test_get_card():
    db = Dictbase()
    p = Player('1', db)
    seq = Sequence([
        Card(CardNumbers.TWO, CardColors.RAINBOW),
        Card(CardNumbers.FOUR, CardColors.WHITE),
        Card(CardNumbers.FIVE, CardColors.BLUE),
        Card(CardNumbers.THREE, CardColors.GREEN),
    ])
    p.start_game(seq)
    p.save()
    p.get_card(0)
    expected = Sequence([
        Card(CardNumbers.FOUR, CardColors.WHITE),
        Card(CardNumbers.FIVE, CardColors.BLUE),
        Card(CardNumbers.THREE, CardColors.GREEN),
    ])
    assert db.get_player_info('1').hand == expected
