from src.models.connection import Connection
from src.models.drone import Drone
from src.routing.graph import Graph


class Simulation:
    """Run the drone movement rules over time.

    It tracks each drone, hub usage, and connection usage while the
    simulation advances from turn to turn.
    """

    def __init__(
        self,
        drones: list[Drone],
        graph: Graph,
    ) -> None:
        """Store the active drones and the map graph."""
        self.drones = drones
        self.graph = graph
        self.time = -1
        self.previous_positions: dict[int, str] = {
            drone.drone_id: drone.current_hub
            for drone in drones
        }

    def run(self) -> None:
        """Advance the simulation until every drone has finished its route."""
        while not self._finished():
            self.step()

    @property
    def finished(self) -> bool:
        """Return whether all drones have completed their assigned route."""
        return self._finished()

    def step(self) -> None:
        """Execute one simulation turn and trigger movement decisions."""
        self.time += 1

        self._complete_travel()
        self.hub_usage = self._get_hub_usage()
        self.link_usage: dict[frozenset[str], int] = {}
        reserved_hubs = self._get_reserved_hubs()
        self.link_usage.update(self._get_travel_link_usage())

        ordered_drones = sorted(
            self.drones,
            key=lambda drone: (
                self._is_priority_drone(drone),
                -drone.drone_id,
            ),
            reverse=True,
        )

        for drone in ordered_drones:
            if drone.finished:
                continue
            if drone.moving:
                continue

            current = drone.current_hub
            next_hub = drone.route.hubs[drone.position + 1]

            if not self._can_move(
                current,
                next_hub,
                self.hub_usage,
                self.link_usage,
                reserved_hubs,
            ):
                continue

            self.previous_positions[drone.drone_id] = current
            link = self._find_connection(current, next_hub)
            if link is None:
                continue

            drone.last_move_cost = self._movement_cost(next_hub)
            drone.travel_remaining = drone.last_move_cost
            self.link_usage[link.key] = self.link_usage.get(link.key, 0) + 1

            if drone.travel_remaining == 1:
                self._finish_drone_move(drone)
                self.hub_usage[current] -= 1
                self.hub_usage[next_hub] = self.hub_usage.get(next_hub, 0) + 1
            else:
                reserved_hubs[next_hub] = reserved_hubs.get(next_hub, 0) + 1

        self._print_state()

    def _print_capacity_info(self) -> None:
        print(f"\nCapacity information - Turn {self.time}")

        for hub in self.graph.fly_map.hubs.values():
            usage = self.hub_usage.get(hub.name, 0)

            if hub.max_drones is not None:
                print(
                    f"Zone {hub.name}: "
                    f"{usage}/{hub.max_drones} drones"
                )

        for connection in self.graph.fly_map.connections:
            usage = self.link_usage.get(connection.key, 0)

            print(
                f"Connection {connection.hub1}-{connection.hub2}: "
                f"{usage}/{connection.max_link_capacity} "
                f"capacity used"
            )

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
        reserved_hubs: dict[str, int],
    ) -> bool:
        hub = self.graph.fly_map.hubs[next_hub]
        if hub.zone == "blocked":
            return False

        if (
            hub.max_drones is not None
            and (
                hub_usage.get(next_hub, 0)
                + reserved_hubs.get(next_hub, 0)
                >= hub.max_drones
            )
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

    def _movement_cost(self, hub_name: str) -> int:
        zone = self.graph.fly_map.hubs[hub_name].zone
        return 2 if zone == "restricted" else 1

    def _complete_travel(self) -> None:
        for drone in self.drones:
            if not drone.moving:
                continue
            drone.travel_remaining -= 1
            if drone.travel_remaining == 0:
                self._finish_drone_move(drone)

    def _finish_drone_move(self, drone: Drone) -> None:
        drone.travel_remaining = 0
        drone.move()

    def _get_reserved_hubs(self) -> dict[str, int]:
        reserved: dict[str, int] = {}
        for drone in self.drones:
            if drone.moving:
                next_hub = drone.route.hubs[drone.position + 1]
                reserved[next_hub] = reserved.get(next_hub, 0) + 1
        return reserved

    def _get_travel_link_usage(self) -> dict[frozenset[str], int]:
        usage: dict[frozenset[str], int] = {}
        for drone in self.drones:
            if drone.moving:
                link = self._find_connection(
                    drone.current_hub,
                    drone.route.hubs[drone.position + 1],
                )
                if link is not None:
                    usage[link.key] = usage.get(link.key, 0) + 1
        return usage

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
        states: list[str] = []

        for drone in self.drones:
            if drone.moving:
                next_hub = drone.route.hubs[drone.position + 1]
                location = f"{drone.current_hub}->{next_hub}"
            else:
                location = drone.current_hub

            states.append(f"D{drone.drone_id}-{location}")

        print(f"{self.time}: {' '.join(states)}")

    def _is_priority_drone(self, drone: Drone) -> bool:
        next_position = drone.position + 1

        if next_position >= len(drone.route.hubs):
            return False

        next_hub = drone.route.hubs[next_position]
        hub = self.graph.fly_map.hubs[next_hub]

        return hub.zone == "priority"

    def get_drone_previous_hub(self, drone_id: int) -> str:
        return self.previous_positions[drone_id]

    def reset(self) -> None:
        for drone in self.drones:
            drone.position = 0
            drone.travel_remaining = 0
            drone.last_move_cost = 1

        self.time = -1

        self.previous_positions = {
            drone.drone_id: drone.current_hub
            for drone in self.drones
        }
