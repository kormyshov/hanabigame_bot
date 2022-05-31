# coding=utf-8
from dataclasses import dataclass, field
from typing import List, Callable

from exceptions import CardIsNotInSequence
from card import (
    Card,
    CardColors as Color,
    CardNumbers as Number,
)


@dataclass
class Sequence:
    lst: List[Card] = field(default_factory=list)

    @classmethod
    def init_full_sequence(cls):
        lst = []
        for color in Color:
            if color == Color.RAINBOW:
                continue
            for count in range(3):
                lst.append(Card(Number.ONE, color))
            for number in (Number.TWO, Number.THREE, Number.FOUR):
                for count in range(2):
                    lst.append(Card(number, color))
            lst.append(Card(Number.FIVE, color))

        for number in Number:
            lst.append(Card(number, Color.RAINBOW))

        return cls(lst)

    def __str__(self) -> str:
        return ' '.join(map(str, self.lst))

    def __contains__(self, card: Card) -> bool:
        return card in self.lst

    def len(self) -> int:
        return len(self.lst)

    def pop(self, index: int = -1) -> Card:
        card = self.lst.pop(index)
        return card

    def append(self, card: Card) -> None:
        self.lst.append(card)

    def index(self, card: Card) -> int:
        try:
            return self.lst.index(card)
        except ValueError:
            raise CardIsNotInSequence

    def get_card_numbers(self, predicate: Callable[[Card], bool]) -> List[int]:
        return [i + 1 for i, card in enumerate(self.lst) if predicate(card)]
