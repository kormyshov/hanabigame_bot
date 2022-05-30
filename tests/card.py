from card import (
    Card,
    CardNumbers,
    CardColors,
)


def test_previous_card_ok():
    a = Card(CardNumbers.FIVE, CardColors.GREEN)
    assert a.get_previous_card() == Card(CardNumbers.FOUR, CardColors.GREEN)


def test_previous_card_for_one():
    a = Card(CardNumbers.ONE, CardColors.RAINBOW)
    assert a.get_previous_card() is None


def test_next_card_ok():
    a = Card(CardNumbers.THREE, CardColors.BLUE)
    assert a.get_next_card() == Card(CardNumbers.FOUR, CardColors.BLUE)


def test_next_card_for_five():
    a = Card(CardNumbers.FIVE, CardColors.YELLOW)
    assert a.get_next_card() is None
