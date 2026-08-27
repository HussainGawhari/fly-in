from dataclasses import dataclass

from src.models.route import Route


@dataclass
class Drone:
    drone_id: int
    route: Route
    position: int = 0
    travel_remaining: int = 0
    last_move_cost: int = 1

    @property
    def current_hub(self) -> str:
        return self.route.hubs[self.position]

    @property
    def finished(self) -> bool:
        return (
            self.position >= len(self.route.hubs) - 1
            and self.travel_remaining == 0
        )

    @property
    def moving(self) -> bool:
        return self.travel_remaining > 0

    def move(self) -> None:
        if not self.finished:
            self.position += 1
