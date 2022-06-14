from sequence import Sequence
from dictbase import Dictbase
from card import (
    Card,
    CardNumbers,
    CardColors,
)
from game import (
    init_list,
    Game,
    TableInfo,
    GameState,
)
from player import Player, PlayerState


def test_init_list():
    lst = init_list()
    assert len(lst) == 55

    s = Sequence(lst)
    assert len(s.get_card_numbers(lambda c: c.number == CardNumbers.ONE)) == 16
    assert len(s.get_card_numbers(lambda c: c.number == CardNumbers.TWO)) == 11
    assert len(s.get_card_numbers(lambda c: c.number == CardNumbers.THREE)) == 11
    assert len(s.get_card_numbers(lambda c: c.number == CardNumbers.FOUR)) == 11
    assert len(s.get_card_numbers(lambda c: c.number == CardNumbers.FIVE)) == 6

    assert len(s.get_card_numbers(lambda c: c.color == CardColors.BLUE)) == 10
    assert len(s.get_card_numbers(lambda c: c.color == CardColors.RED)) == 10
    assert len(s.get_card_numbers(lambda c: c.color == CardColors.GREEN)) == 10
    assert len(s.get_card_numbers(lambda c: c.color == CardColors.YELLOW)) == 10
    assert len(s.get_card_numbers(lambda c: c.color == CardColors.WHITE)) == 10
    assert len(s.get_card_numbers(lambda c: c.color == CardColors.RAINBOW)) == 5


def test_get_table_info_empty():
    g = Game()
    assert g.get_table_info() == TableInfo(Sequence(), 0, 0)


def test_get_table_info_started():
    g = Game()
    g.start()
    assert g.get_table_info() == TableInfo(Sequence(), 8, 3)
    Game.clear()


def test_get_table_info_add_to_table():
    g = Game()
    g.start()
    a = Card(CardNumbers.ONE, CardColors.RAINBOW)
    g.add_to_table(a)
    assert g.get_table_info() == TableInfo(Sequence([a]), 8, 3)
    Game.clear()


def test_get_table_info_add_to_table_twice():
    g = Game()
    g.start()
    a = Card(CardNumbers.ONE, CardColors.RAINBOW)
    b = Card(CardNumbers.TWO, CardColors.RAINBOW)
    g.add_to_table(a)
    g.add_to_table(b)
    assert g.get_table_info() == TableInfo(Sequence([b]), 8, 3)
    Game.clear()


def test_get_trash_cards_empty():
    g = Game()
    assert g.get_trash_cards() == Sequence()


def test_start_game():
    g = Game()
    db = Dictbase()
    p1 = Player('1', db)
    p2 = Player('2', db)
    g.players = [p1, p2]
    g.start()
    assert p1.state == PlayerState.PLAYING
    assert p2.state == PlayerState.PLAYING
    assert p1.hand.len() == 5
    assert p2.hand.len() == 5
    assert g.state == GameState.TURN_PLAYER_ONE
    assert g.hints == 8
    assert g.lives == 3
    assert g.trash.len() == 0
    assert g.table.len() == 0
    assert g.stack.len() == 45
    Game.clear()


def test_take_card():
    g = Game()
    db = Dictbase()
    p1 = Player('1', db)
    p2 = Player('2', db)
    g.players = [p1, p2]
    g.start()
    c1 = g.stack.lst[-1]
    c2 = g.take_card()
    assert g.stack.len() == 44
    assert c1 == c2
    Game.clear()


def test_move_card_to_player():
    g = Game()
    db = Dictbase()
    p1 = Player('1', db)
    p2 = Player('2', db)
    g.players = [p1, p2]
    g.start()
    c1 = g.stack.lst[-1]
    g.move_card_to_player(p1)
    assert g.stack.len() == 44
    assert p1.hand.len() == 6
    assert p1.hand.lst[-1] == c1
    Game.clear()


def test_move_to_trash():
    g = Game()
    db = Dictbase()
    p1 = Player('1', db)
    p2 = Player('2', db)
    g.players = [p1, p2]
    g.start()
    c1 = p1.hand.lst[1]
    c2 = g.stack.lst[-1]
    g.move_to_trash(p1, 1)
    assert g.trash == Sequence([c1])
    assert p1.hand.lst[-1] == c2
    assert g.stack.len() == 44
    Game.clear()
