from dataclasses import dataclass

from src.models.route import Route


@dataclass
class Drone:
    """Models one autonomous drone moving along a predefined route.

    It tracks the current hub, travel progress, and whether it is waiting for a
    movement to finish before advancing.
    """

    drone_id: int
    route: Route
    position: int = 0
    travel_remaining: int = 0
    last_move_cost: int = 1

    @property
    def current_hub(self) -> str:
        """Return the hub the drone is currently occupying."""
        return self.route.hubs[self.position]

    @property
    def finished(self) -> bool:
        """Return whether the drone has completed all assigned travel."""
        return (
            self.position >= len(self.route.hubs) - 1
            and self.travel_remaining == 0
        )

    @property
    def moving(self) -> bool:
        """Return whether the drone is still traversing a connection."""
        return self.travel_remaining > 0

    def move(self) -> None:
        """Advance the drone when the current trip is complete.

        The movement is only committed if the drone is not already finished.
        """
        if not self.finished:
            self.position += 1
