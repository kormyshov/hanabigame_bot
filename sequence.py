# coding=utf-8
from dataclasses import dataclass, field
from typing import List, Callable

from exceptions import CardIsNotInSequence
from card import Card, CardNumbers, CardColors


@dataclass
class Sequence:
    lst: List[Card] = field(default_factory=list)

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


# from pickle import dumps, loads
# from base64 import b64decode, b64encode
#
#
# def foo():
#     s = Sequence([Card(CardNumbers.FOUR, CardColors.YELLOW), Card(CardNumbers.ONE, CardColors.WHITE)])
#     return b64encode(dumps(s))
#
#
# d = foo()
# print(d)
# t = loads(b64decode(d))
# print(t)