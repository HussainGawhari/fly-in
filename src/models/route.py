from dataclasses import dataclass


@dataclass
class Route:
    hubs: list[str]

    @property
    def length(self) -> int:
        return len(self.hubs) - 1
