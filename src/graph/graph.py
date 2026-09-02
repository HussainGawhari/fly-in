from src.models.map import FlyMap


class Graph:
    """Adjacency-based graph for the map connectivity used by route finding."""

    def __init__(self, fly_map: FlyMap) -> None:
        """Build the neighbor map from the parsed FlyMap definition."""
        self.fly_map = fly_map
        self.adjacency: dict[str, list[str]] = {}

        self._build()

    def _build(self) -> None:
        """Initialize all hub entries and link each pair of connected hubs."""
        for hub_name in self.fly_map.hubs:
            self.adjacency[hub_name] = []

        for connection in self.fly_map.connections:
            self.adjacency[connection.hub1].append(connection.hub2)
            self.adjacency[connection.hub2].append(connection.hub1)

    def neighbors(self, hub_name: str) -> list[str]:
        """Return all reachable hubs adjacent to the given hub."""
        return self.adjacency[hub_name]
