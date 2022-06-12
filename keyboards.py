from typing import List, Tuple
import constants


def get_start_game() -> Tuple[str, ...]:
    return (
        constants.CREATE_GAME,
        constants.CONNECT_TO_GAME,
    )


def get_waiting_second_player() -> Tuple[str, ...]:
    return (
        constants.FINISH_GAME,
    )


def get_confirm_finish_game() -> Tuple[str, ...]:
    return (
        constants.YES_FINISH_GAME,
        constants.NO_CONTINUE_GAME,
    )


def get_reject_connect_game() -> Tuple[str, ...]:
    return (
        constants.DONT_CONNECT_TO_GAME,
    )


def get_waiting_start_game() -> Tuple[str, ...]:
    return (
        constants.START_GAME,
        constants.FINISH_GAME,
    )


def get_waiting_turn() -> Tuple[str, ...]:
    return (
        constants.LOOK_HANDS,
        constants.LOOK_TABLE,
        constants.LOOK_TRASH,
        constants.FINISH_GAME,
    )


def get_turn() -> Tuple[str, ...]:
    return (
        constants.PUT,
        constants.TRASH,
        constants.HINT,
        constants.LOOK_HANDS,
        constants.LOOK_TABLE,
        constants.LOOK_TRASH,
        constants.FINISH_GAME,
    )


def get_type_of_hint() -> Tuple[str, ...]:
    return (
        constants.COLOR,
        constants.VALUE,
        constants.BACK,
    )


def get_colors() -> Tuple[str, ...]:
    return (
        constants.GREEN,
        constants.RED,
        constants.BLUE,
        constants.YELLOW,
        constants.WHITE,
        constants.BACK,
    )


def get_values() -> Tuple[str, ...]:
    return (
        constants.ONE,
        constants.TWO,
        constants.THREE,
        constants.FOUR,
        constants.FIVE,
        constants.BACK,
    )


def get_request_card_number(count_of_cards: int) -> List[str]:
    keyboard = []
    for i in range(1, count_of_cards + 1):
        keyboard.append(str(i))
    keyboard.append(constants.BACK)
    return keyboard


def get_request_player_name(names: List[str]) -> List[str]:
    keyboard = []
    for name in names:
        keyboard.append(name)
    keyboard.append(constants.BACK)
    return keyboard
