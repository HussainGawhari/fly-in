from src.models.connection import Connection
from src.models.drone import Drone
from src.graph.graph import Graph


class Simulation:
    """Run the drone simulation."""

    TERMINAL_COLORS = {
        "red": "31",
        "darkred": "31",
        "crimson": "31",
        "green": "32",
        "yellow": "33",
        "orange": "33",
        "brown": "33",
        "gold": "33",
        "blue": "34",
        "purple": "35",
        "violet": "35",
        "cyan": "36",
        "maroon": "31",
        "gray": "90",
        "grey": "90",
        "white": "97",
        "black": "30",
    }

    def __init__(
        self,
        drones: list[Drone],
        graph: Graph,
    ) -> None:
        self.drones = drones
        self.graph = graph
        self.time = 0
        self.current_turn_movements: list[str] = []

        self.previous_positions = {
            drone.drone_id: drone.current_hub
            for drone in drones
        }

        self.hub_usage: dict[str, int] = {}
        self.link_usage: dict[frozenset[str], int] = {}

    def run(self) -> None:
        while not self.finished:
            self.step()

    @property
    def finished(self) -> bool:
        return all(drone.finished for drone in self.drones)

    def step(self) -> None:
        self.time += 1
        self.current_turn_movements = []

        self._complete_travel()

        self.hub_usage = self._get_hub_usage()
        self.link_usage = self._get_travel_link_usage()
        reserved_hubs = self._get_reserved_hubs()

        drones = sorted(
            self.drones,
            key=lambda drone: (
                self._is_priority_drone(drone),
                -drone.drone_id,
            ),
            reverse=True,
        )

        for drone in drones:
            if drone.finished or drone.moving:
                continue

            next_position = drone.position + 1

            if next_position >= len(drone.route.hubs):
                continue

            current = drone.current_hub
            next_hub = drone.route.hubs[next_position]
            connection = self._find_connection(current, next_hub)

            if connection is None:
                continue

            if not self._can_move(
                next_hub,
                connection,
                reserved_hubs,
            ):
                continue

            self.previous_positions[drone.drone_id] = current

            drone.travel_remaining = self._movement_cost(next_hub)

            self.link_usage[connection.key] = (
                self.link_usage.get(connection.key, 0) + 1
            )

            if drone.travel_remaining == 1:
                self._finish_drone_move(drone)

                self.hub_usage[current] -= 1
                self.hub_usage[next_hub] = (
                    self.hub_usage.get(next_hub, 0) + 1
                )

                self._record_movement(
                    drone,
                    next_hub,
                )
            else:
                reserved_hubs[next_hub] = (
                    reserved_hubs.get(next_hub, 0) + 1
                )

                self._record_movement(
                    drone,
                    self._connection_name(connection),
                )
        self._print_turn()

    def _complete_travel(self) -> None:
        """Complete movements that were started in previous turns."""
        for drone in self.drones:
            if not drone.moving:
                continue

            drone.travel_remaining -= 1

            if drone.travel_remaining == 0:
                self._finish_drone_move(drone)
                self._record_movement(
                    drone,
                    drone.current_hub,
                )

    def _record_movement(
        self,
        drone: Drone,
        destination: str,
    ) -> None:
        """Record one drone movement."""
        text = f"D{drone.drone_id}-{destination}"
        hub = self.graph.fly_map.hubs.get(destination)

        if hub is not None:
            color = self.TERMINAL_COLORS.get(
                (hub.color or "").lower()
            )

            if color:
                text = f"\033[{color}m{text}\033[0m"

        self.current_turn_movements.append(text)

    def _print_turn(self) -> None:
        """Print the turn number and movements."""
        if not self.current_turn_movements:
            return

        print(f"Turn {self.time}")
        print(" ".join(self.current_turn_movements))
        print()

    def _get_hub_usage(self) -> dict[str, int]:
        """Count drones currently occupying each hub."""
        usage: dict[str, int] = {}

        for drone in self.drones:
            if drone.finished:
                continue
            hub = drone.current_hub
            usage[hub] = usage.get(hub, 0) + 1

        return usage

    def _get_reserved_hubs(self) -> dict[str, int]:
        """Count destination hubs reserved by drones in flight."""
        reserved: dict[str, int] = {}

        for drone in self.drones:
            if not drone.moving:
                continue

            next_position = drone.position + 1

            if next_position >= len(drone.route.hubs):
                continue

            next_hub = drone.route.hubs[next_position]
            reserved[next_hub] = reserved.get(next_hub, 0) + 1
        return reserved

    def _get_travel_link_usage(
        self,
    ) -> dict[frozenset[str], int]:
        """Count connections currently used by drones in flight."""
        usage: dict[frozenset[str], int] = {}

        for drone in self.drones:
            if not drone.moving:
                continue

            next_position = drone.position + 1

            if next_position >= len(drone.route.hubs):
                continue

            next_hub = drone.route.hubs[next_position]
            connection = self._find_connection(
                drone.current_hub,
                next_hub,
            )

            if connection is not None:
                usage[connection.key] = (
                    usage.get(connection.key, 0) + 1
                )
        return usage

    def _can_move(
        self,
        next_hub: str,
        connection: Connection,
        reserved_hubs: dict[str, int],
    ) -> bool:
        """Check hub and connection capacity."""
        hub = self.graph.fly_map.hubs[next_hub]

        if hub.zone == "blocked":
            return False

        if hub.max_drones is not None:
            occupied = self.hub_usage.get(next_hub, 0)
            reserved = reserved_hubs.get(next_hub, 0)

            if occupied + reserved >= hub.max_drones:
                return False

        capacity = connection.max_link_capacity

        if capacity is not None:
            used = self.link_usage.get(connection.key, 0)

            if used >= capacity:
                return False
        return True

    def _movement_cost(self, hub_name: str) -> int:
        if self.graph.fly_map.hubs[hub_name].zone == "restricted":
            return 2
        return 1

    def _finish_drone_move(self, drone: Drone) -> None:
        drone.travel_remaining = 0
        drone.move()

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

    def _connection_name(self, connection: Connection) -> str:
        name = getattr(connection, "name", None)

        if name:
            return str(name)

        return f"{connection.hub1}-{connection.hub2}"

    def _is_priority_drone(self, drone: Drone) -> bool:
        next_position = drone.position + 1

        if next_position >= len(drone.route.hubs):
            return False

        next_hub = drone.route.hubs[next_position]

        return (
            self.graph.fly_map.hubs[next_hub].zone == "priority"
        )

    def get_drone_previous_hub(self, drone_id: int) -> str:
        return self.previous_positions[drone_id]

    def reset(self) -> None:
        for drone in self.drones:
            drone.position = 0
            drone.travel_remaining = 0
            drone.last_move_cost = 1

        self.time = 0
        self.current_turn_movements = []

        self.previous_positions = {
            drone.drone_id: drone.current_hub
            for drone in self.drones
        }

        self.hub_usage = {}
        self.link_usage = {}
