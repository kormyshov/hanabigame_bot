from abc import ABC, abstractmethod
from typing import Iterable, Optional


class AbstractViewer(ABC):
    @abstractmethod
    def view(self, player_id: str, message: str, keyboard: Optional[Iterable[str]] = None) -> None:
        pass
