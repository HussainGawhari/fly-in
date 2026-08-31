from src.models.drone import Drone
from src.models.route import Route


class Scheduler:
    """Assign routes to drone instances.

    The scheduler uses a round-robin policy so drones are spread across the
    available paths.
    """

    def __init__(self, routes: list[Route], nb_drones: int) -> None:
        """Store the route pool and number of drones to create."""
        self.routes = routes
        self.nb_drones = nb_drones

    def create_drones(self) -> list[Drone]:
        """Create drone instances distributed across the available routes."""
        drones: list[Drone] = []

        for drone_id in range(1, self.nb_drones + 1):
            route = self.routes[(drone_id - 1) % len(self.routes)]
            drones.append(Drone(drone_id, route))

        return drones
