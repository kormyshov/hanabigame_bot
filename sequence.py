# coding=utf-8
import logging


def num_to_emoji(num):
    return ['💙', '💚', '❤️', '🤍', '💛', '💖'][num]


def emoji_to_num(emoji):
    return ['💙', '💚', '❤️', '🤍', '💛', '💖'].index(emoji)


def num_to_card(num):
    k = num % 5
    m = num // 5
    return str(k + 1) + num_to_emoji(m)


def is_color(card_number, color_number):
    return (card_number // 5) == color_number or (card_number // 5) == 5


def is_value(card_number, value):
    return card_number % 5 == int(value) - 1


def previous_card(num):
    if num % 5 == 0:
        return None
    return num - 1


def next_card(num):
    if num % 5 == 4:
        return None
    return num + 1


def init_list():
    return [0, 5, 10, 15, 20] * 3 + [1, 2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18, 21, 22, 23] * 2 + [4, 9, 14, 19, 24] + [
        25, 26, 27, 28, 29]


class Sequence:

    def __init__(self, lst):
        self.lst = lst

    @classmethod
    def from_str(cls, s):
        if s is None or s == '':
            return None
        return cls(list(map(int, s.split())))

    def to_str(self):
        if self.lst is None:
            return None
        return ' '.join(map(str, self.lst))

    def to_output(self):
        if self.lst is None:
            return ''
        return ' '.join(map(num_to_card, self.lst))

    def len(self):
        return len(self.lst) if self.lst is not None else 0

    def pop(self, index=-1):
        logger = logging.getLogger('hanabigame.sequence.pop')
        logger.info('start')
        num = self.lst.pop(index)
        logger.info('get num ' + str(num))
        return num

    def append(self, num):
        self.lst.append(num)

    def contains(self, num):
        return self.lst is not None and num in self.lst

    def index(self, num):
        return self.lst.index(num)

    def get_card_numbers_with_color(self, color):
        num = emoji_to_num(color)
        return [i + 1 for i, card in enumerate(self.lst) if is_color(card, num)]

    def get_card_numbers_with_value(self, value):
        return [i + 1 for i, card in enumerate(self.lst) if is_value(card, value)]
