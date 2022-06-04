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
)


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


def test_get_trash_cards():
    g = Game()
    a = Card(CardNumbers.ONE, CardColors.RAINBOW)
    g.add_to_trash(a)
    assert g.get_trash_cards() == Sequence([a])
    Game.clear()


def test_get_trash_cards_many():
    g = Game()
    a = Card(CardNumbers.ONE, CardColors.RAINBOW)
    b = Card(CardNumbers.TWO, CardColors.RAINBOW)
    g.add_to_trash(a)
    g.add_to_trash(b)
    g.add_to_trash(a)
    assert g.get_trash_cards() == Sequence([a, b, a])
    Game.clear()
