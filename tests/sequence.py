import pytest
from sequence import Sequence
from exceptions import CardIsNotInSequence
from card import (
    Card,
    CardNumbers,
    CardColors,
)


def test_len_empty():
    s = Sequence()
    assert s.len() == 0


def test_len_ok():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    s = Sequence([a, b])
    assert s.len() == 2


def test_pop_last_element():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    s = Sequence([a, b])
    c = s.pop()
    assert s == Sequence([a])
    assert b == c


def test_pop_first_element():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    s = Sequence([a, b])
    c = s.pop(0)
    assert s == Sequence([b])
    assert a == c


def test_pop_from_empty():
    s = Sequence()
    with pytest.raises(IndexError):
        s.pop()


def test_append_to_empty():
    s = Sequence()
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    s.append(a)
    assert s == Sequence([a])


def test_append():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    s = Sequence([a])
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    s.append(b)
    assert s == Sequence([a, b])


def test_index_ok():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    s = Sequence([a, b])
    c = s.index(Card(CardNumbers.ONE, CardColors.BLUE))
    assert c == 0


def test_index_fail():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    s = Sequence([a, b])
    with pytest.raises(CardIsNotInSequence):
        s.index(Card(CardNumbers.ONE, CardColors.YELLOW))


def test_get_card_numbers_all():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    c = Card(CardNumbers.FIVE, CardColors.BLUE)
    s = Sequence([a, b, c])
    assert s.get_card_numbers(lambda _: True) == [1, 2, 3]


def test_get_card_numbers_with_color():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    c = Card(CardNumbers.FIVE, CardColors.BLUE)
    s = Sequence([a, b, c])
    assert s.get_card_numbers(lambda card: card.color == CardColors.BLUE) == [1, 3]


def test_get_card_numbers_with_number():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    c = Card(CardNumbers.FIVE, CardColors.BLUE)
    s = Sequence([a, b, c])
    assert s.get_card_numbers(lambda card: card.number == CardNumbers.FIVE) == [2, 3]


def test_get_card_numbers_empty():
    a = Card(CardNumbers.ONE, CardColors.BLUE)
    b = Card(CardNumbers.FIVE, CardColors.YELLOW)
    c = Card(CardNumbers.FIVE, CardColors.BLUE)
    s = Sequence([a, b, c])
    assert s.get_card_numbers(lambda _: False) == []
