from dataclasses import dataclass

from src.models.route import Route


@dataclass
class Drone:
    drone_id: int
    route: Route
    position: int = 0

    @property
    def current_hub(self) -> str:
        return self.route.hubs[self.position]

    @property
    def finished(self) -> bool:
        return self.position >= len(self.route.hubs) - 1

    def move(self) -> None:
        if not self.finished:
            self.position += 1
