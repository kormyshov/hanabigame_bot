from dictbase import Dictbase
from null_viewer import NullViewer, ViewORM
from controller import Controller
from game import Game
import constants
import keyboards


def test_create_game():
    db = Dictbase()
    viewer = NullViewer()
    controller = Controller(db, viewer)
    controller.operate('1', 'Oscar', constants.CREATE_GAME)
    game_id = db.get_player_info('1').game_id
    expected = [
        ViewORM('1', constants.GAME_CREATED, None),
        ViewORM('1', game_id, keyboards.get_waiting_second_player()),
    ]
    assert viewer.get_output() == expected
    Game.clear()


def test_create_and_request_finish_game():
    db = Dictbase()
    viewer = NullViewer()
    controller = Controller(db, viewer)
    controller.operate('1', 'Oscar', constants.CREATE_GAME)
    controller.operate('1', 'Oscar', constants.FINISH_GAME)
    game_id = db.get_player_info('1').game_id
    expected = [
        ViewORM('1', constants.GAME_CREATED, None),
        ViewORM('1', game_id, keyboards.get_waiting_second_player()),
        ViewORM('1', constants.ARE_YOU_SURE, keyboards.get_confirm_finish_game()),
    ]
    assert viewer.get_output() == expected
    Game.clear()


def test_create_and_request_finish_game_reject():
    db = Dictbase()
    viewer = NullViewer()
    controller = Controller(db, viewer)
    controller.operate('1', 'Oscar', constants.CREATE_GAME)
    controller.operate('1', 'Oscar', constants.FINISH_GAME)
    controller.operate('1', 'Oscar', constants.NO_CONTINUE_GAME)
    game_id = db.get_player_info('1').game_id
    expected = [
        ViewORM('1', constants.GAME_CREATED, None),
        ViewORM('1', game_id, keyboards.get_waiting_second_player()),
        ViewORM('1', constants.ARE_YOU_SURE, keyboards.get_confirm_finish_game()),
        ViewORM('1', constants.LETS_CONTINUE, keyboards.get_waiting_second_player()),
    ]
    assert viewer.get_output() == expected
    Game.clear()


def test_create_and_request_finish_game_confirm():
    db = Dictbase()
    viewer = NullViewer()
    controller = Controller(db, viewer)
    controller.operate('1', 'Oscar', constants.CREATE_GAME)
    game_id = db.get_player_info('1').game_id
    controller.operate('1', 'Oscar', constants.FINISH_GAME)
    controller.operate('1', 'Oscar', constants.YES_FINISH_GAME)
    expected = [
        ViewORM('1', constants.GAME_CREATED, None),
        ViewORM('1', game_id, keyboards.get_waiting_second_player()),
        ViewORM('1', constants.ARE_YOU_SURE, keyboards.get_confirm_finish_game()),
        ViewORM('1', constants.GAME_FINISHED, keyboards.get_start_game()),
    ]
    assert viewer.get_output() == expected
    assert len(db.games) == 0
    assert len(db.players) == 0
    Game.clear()


def test_connect_game():
    db = Dictbase()
    viewer = NullViewer()
    controller = Controller(db, viewer)
    controller.operate('1', 'Oscar', constants.CONNECT_TO_GAME)
    expected = [ViewORM('1', constants.ENTER_GAME_CODE_TO_CONNECT, keyboards.get_reject_connect_game())]
    assert viewer.get_output() == expected
    Game.clear()


def test_connect_and_reject_game():
    db = Dictbase()
    viewer = NullViewer()
    controller = Controller(db, viewer)
    controller.operate('1', 'Oscar', constants.CONNECT_TO_GAME)
    controller.operate('1', 'Oscar', constants.DONT_CONNECT_TO_GAME)
    expected = [
        ViewORM('1', constants.ENTER_GAME_CODE_TO_CONNECT, keyboards.get_reject_connect_game()),
        ViewORM('1', constants.ONBOARDING, keyboards.get_start_game()),
    ]
    assert viewer.get_output() == expected
    Game.clear()


def test_create_and_connect_game():
    db = Dictbase()
    viewer = NullViewer()
    controller = Controller(db, viewer)
    controller.operate('1', 'Oscar', constants.CREATE_GAME)
    game_id = db.get_player_info('1').game_id
    controller.operate('2', 'Lucky', constants.CONNECT_TO_GAME)
    controller.operate('2', 'Lucky', game_id)
    expected = [
        ViewORM('1', constants.GAME_CREATED, None),
        ViewORM('1', game_id, keyboards.get_waiting_second_player()),
        ViewORM('2', constants.ENTER_GAME_CODE_TO_CONNECT, keyboards.get_reject_connect_game()),
        ViewORM('1', constants.PLAYER_CONNECT_TO_GAME.format('Lucky'), keyboards.get_waiting_start_game()),
        ViewORM('2', constants.YOU_HAS_BEEN_CONNECTED_TO_GAME, keyboards.get_waiting_start_game()),
    ]
    assert viewer.get_output() == expected
    Game.clear()
