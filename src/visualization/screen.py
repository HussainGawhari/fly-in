from typing import Protocol


class Screen(Protocol):
    def get_size(self) -> tuple[int, int]:
        ...

    def blit(self, source: object, dest: object) -> object:
        ...
