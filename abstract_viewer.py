from typing import Iterable, Optional


class AbstractViewer:
    def view(self, player_id: str, message: str, keyboard: Optional[Iterable[str]] = None) -> None:
        raise NotImplementedError
