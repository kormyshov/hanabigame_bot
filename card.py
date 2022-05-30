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
