from src.models.map import FlyMap


class Graph:
    def __init__(self, fly_map: FlyMap) -> None:
        self.fly_map = fly_map
        self.adjacency: dict[str, list[str]] = {}

        self._build()

    def _build(self) -> None:
        for hub_name in self.fly_map.hubs:
            self.adjacency[hub_name] = []

        for connection in self.fly_map.connections:
            self.adjacency[connection.hub1].append(connection.hub2)
            self.adjacency[connection.hub2].append(connection.hub1)

    def neighbors(self, hub_name: str) -> list[str]:
        return self.adjacency[hub_name]
