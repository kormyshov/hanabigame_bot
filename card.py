# coding=utf-8
from __future__ import annotations
from typing import NamedTuple
from enum import Enum


class CardNumbers(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class CardColors(Enum):
    BLUE = '💙'
    GREEN = '💚'
    RED = '❤️'
    WHITE = '🤍'
    YELLOW = '💛'
    RAINBOW = '💖'


class Card(NamedTuple):
    number: CardNumbers
    color: CardColors

    def get_previous_card(self) -> Card:
        if self.number == CardNumbers.ONE:
            raise DontExistCard
        return Card(CardNumbers(self.number.value - 1), self.color)

    def get_next_card(self) -> Card:
        if self.number == CardNumbers.FIVE:
            raise DontExistCard
        return Card(CardNumbers(self.number.value + 1), self.color)

    def __str__(self) -> str:
        return str(self.number.value) + self.color.value


class DontExistCard(Exception):
    pass
