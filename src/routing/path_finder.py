import heapq

from src.models.route import Route
from src.routing.graph import Graph


class Pathfinder:
    """Find the best route while respecting map restrictions.

    The path finder uses a priority queue and applies hub-based costs to decide
    which route should be explored first.
    """

    def __init__(self, graph: Graph) -> None:
        """Store the graph used for path selection."""
        self.graph = graph

    def find_path(self, start: str, goal: str) -> list[str] | None:
        """Return the lowest-cost path between two hubs.

        If no valid route exists, the method returns None.
        """
        queue: list[tuple[int, int, str]] = [(0, 0, start)]
        best_cost: dict[str, tuple[int, int]] = {start: (0, 0)}
        parent: dict[str, str | None] = {start: None}

        while queue:
            turns, priority_penalty, current = heapq.heappop(queue)

            if current == goal:
                return self._build_path(parent, goal)

            for neighbor in self.graph.neighbors(current):
                if self.graph.fly_map.hubs[neighbor].zone == "blocked":
                    continue
                next_cost = (
                    turns + self._movement_cost(neighbor),
                    priority_penalty + self._priority_penalty(neighbor),
                )
                if next_cost >= best_cost.get(
                    neighbor,
                    (float("inf"), float("inf")),
                ):
                    continue
                best_cost[neighbor] = next_cost
                parent[neighbor] = current
                heapq.heappush(queue, (*next_cost, neighbor))

        return None

    def find_paths(
        self,
        start: str,
        goal: str,
        max_paths: int = 5,
    ) -> list[Route]:
        """Return a list of route objects for the given start and goal."""
        path = self.find_path(start, goal)
        if path is None:
            return []

        return [Route(path)]

    def _build_path(
        self,
        parent: dict[str, str | None],
        goal: str,
    ) -> list[str]:
        """Reconstruct the final route from the parent map.

        This method walks backward from the destination until the start hub is
        reached, then reverses the list.
        """
        path: list[str] = []
        current: str | None = goal

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()
        return path

    def find_best_paths(
        self,
        start: str,
        goal: str,
        max_paths: int = 5,
    ) -> list[Route]:
        """Return the preferred route list for the solver."""
        return self.find_paths(start, goal, max_paths)

    def _movement_cost(self, hub_name: str) -> int:
        """Return the travel cost for entering a hub zone."""
        zone = self.graph.fly_map.hubs[hub_name].zone
        return 2 if zone == "restricted" else 1

    def _priority_penalty(self, hub_name: str) -> int:
        """Prefer priority hubs during tie-breaking.

        Priority hubs get a lower penalty, making them more attractive when
        costs are equal.
        """
        return 0 if self.graph.fly_map.hubs[hub_name].zone == "priority" else 1
