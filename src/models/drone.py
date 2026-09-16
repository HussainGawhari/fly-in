from dataclasses import dataclass

from src.models.route import Route


@dataclass
class Drone:
    """Represent a drone moving along a predefined route."""

    drone_id: int
    route: Route
    position: int = 0
    travel_remaining: int = 0
    last_move_cost: int = 1

    @property
    def current_hub(self) -> str:
        return self.route.hubs[self.position]

    @property
    def moving(self) -> bool:
        return self.travel_remaining > 0

    @property
    def finished(self) -> bool:
        return (
            self.position == len(self.route.hubs) - 1
            and not self.moving
        )

    def move(self) -> None:
        """Complete the current movement and enter the next hub."""
        if self.position < len(self.route.hubs) - 1:
            self.position += 1
        self.travel_remaining = 0
