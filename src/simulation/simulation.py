from src.models.connection import Connection
from src.models.drone import Drone
from src.models.hub import Hub
from src.routing.graph import Graph


class Simulation:
    def __init__(
        self,
        drones: list[Drone],
        graph: Graph,
    ) -> None:
        self.drones = drones
        self.graph = graph
        self.time = 0

    def run(self) -> None:
        while not self._finished():
            self._step()

    def _step(self) -> None:
        self.time += 1

        hub_usage = self._get_hub_usage()
        link_usage: dict[frozenset[str], int] = {}

        for drone in self.drones:
            if drone.finished:
                continue

            current = drone.current_hub
            next_hub = drone.route.hubs[drone.position + 1]

            if not self._can_move(
                current,
                next_hub,
                hub_usage,
                link_usage,
            ):
                continue

            drone.move()

            hub_usage[current] -= 1
            hub_usage[next_hub] = hub_usage.get(next_hub, 0) + 1

            link = self._find_connection(current, next_hub)

            if link is not None:
                link_usage[link.key] = link_usage.get(link.key, 0) + 1

        self._print_state()

    def _get_hub_usage(self) -> dict[str, int]:
        usage: dict[str, int] = {}

        for drone in self.drones:
            hub = drone.current_hub
            usage[hub] = usage.get(hub, 0) + 1

        return usage

    def _can_move(
        self,
        current: str,
        next_hub: str,
        hub_usage: dict[str, int],
        link_usage: dict[frozenset[str], int],
    ) -> bool:
        hub = self.graph.fly_map.hubs[next_hub]
        if hub.zone == "blocked":
            return False

        if hub.zone == "restricted":
            if hub_usage.get(next_hub, 0) >= 1:
                return False

        if (
            hub.max_drones is not None
            and hub_usage.get(next_hub, 0) >= hub.max_drones
        ):
            return False

        connection = self._find_connection(current, next_hub)

        if connection is None:
            return False

        capacity = connection.max_link_capacity

        if capacity is not None:
            if link_usage.get(connection.key, 0) >= capacity:
                return False

        return True

    def _find_connection(
        self,
        hub1: str,
        hub2: str,
    ) -> Connection | None:
        key = frozenset((hub1, hub2))

        for connection in self.graph.fly_map.connections:
            if connection.key == key:
                return connection

        return None

    def _finished(self) -> bool:
        return all(drone.finished for drone in self.drones)

    def _print_state(self) -> None:
        for drone in self.drones:
            print(
                f"{self.time}: "
                f"Drone {drone.drone_id} "
                f"at {drone.current_hub}"
            )
