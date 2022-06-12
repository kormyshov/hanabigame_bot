from typing import NamedTuple, List
from abstract_viewer import AbstractViewer, Iterable, Optional


class ViewORM(NamedTuple):
    player_id: str
    message: str
    keyboard: Optional[Iterable[str]]


class NullViewer(AbstractViewer):
    def __init__(self):
        self.output: List[ViewORM] = []

    def view(self, player_id: str, message: str, keyboard: Optional[Iterable[str]] = None) -> None:
        self.output.append(ViewORM(player_id, message, keyboard))

    def get_output(self) -> List[ViewORM]:
        return self.output
