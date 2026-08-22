from src.models.drone import Drone
from src.models.route import Route


class Scheduler:

    def __init__(self, routes: list[Route], nb_drones: int) -> None:
        self.routes = routes
        self.nb_drones = nb_drones

    def create_drones(self) -> list[Drone]:
        drones: list[Drone] = []

        for drone_id in range(1, self.nb_drones + 1):
            route = self.routes[(drone_id - 1) % len(self.routes)]
            drones.append(Drone(drone_id, route))

        return drones
