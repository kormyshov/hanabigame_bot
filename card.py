# coding=utf-8
from dataclasses import dataclass


class CardNumbers:
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class CardColors:
    BLUE = '💙'
    GREEN = '💚'
    RED = '❤️'
    WHITE = '🤍'
    YELLOW = '💛'
    RAINBOW = '💖'


@dataclass
class Card:
    number: int
    color: str

    def get_previous_card(self):
        if self.number == CardNumbers.ONE:
            return None
        return Card(self.number - 1, self.color)

    def get_next_card(self):
        if self.number == CardNumbers.FIVE:
            return None
        return Card(self.number + 1, self.color)


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
