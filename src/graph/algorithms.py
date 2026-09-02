from src.models.route import Route
from src.graph.graph import Graph


class _PriorityQueue:
    """Small priority queue used by the Dijkstra path search."""

    def __init__(self) -> None:
        self._items: list[tuple[tuple[int, int], str]] = []

    def put(self, cost: tuple[int, int], hub_name: str) -> None:
        index = 0
        while index < len(self._items) and self._items[index][0] <= cost:
            index += 1
        self._items.insert(index, (cost, hub_name))

    def get(self) -> tuple[tuple[int, int], str]:
        return self._items.pop(0)

    def __bool__(self) -> bool:
        return bool(self._items)


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
        return self._search(start, goal, {})

    def _search(
        self,
        start: str,
        goal: str,
        extra_cost: dict[str, int],
    ) -> list[str] | None:
        """Run Dijkstra while optionally discouraging used hubs."""
        queue = _PriorityQueue()
        best_cost: dict[str, tuple[int, int]] = {start: (0, 0)}
        parent: dict[str, str | None] = {start: None}
        queue.put((0, 0), start)

        while queue:
            current_cost, current = queue.get()
            if current_cost != best_cost[current]:
                continue

            if current == goal:
                return self._build_path(parent, goal)

            for neighbor in self.graph.neighbors(current):
                if self.graph.fly_map.hubs[neighbor].zone == "blocked":
                    continue
                next_cost = (
                    current_cost[0]
                    + self._movement_cost(neighbor)
                    + extra_cost.get(neighbor, 0),
                    current_cost[1] + self._priority_penalty(neighbor),
                )
                if next_cost >= best_cost.get(
                    neighbor,
                    (float("inf"), float("inf")),
                ):
                    continue
                best_cost[neighbor] = next_cost
                parent[neighbor] = current
                queue.put(next_cost, neighbor)

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
        first_path = self.find_path(start, goal)
        if first_path is None:
            return []

        if self.graph.fly_map.nb_drones <= 1 or max_paths <= 1:
            return [Route(first_path)]

        routes = [first_path]
        extra_cost: dict[str, int] = {}

        for _ in range(max_paths - 1):
            for hub_name in routes[-1][1:-1]:
                extra_cost[hub_name] = extra_cost.get(hub_name, 0) + 8

            path = self._search(start, goal, extra_cost)
            if path is None or path in routes:
                break
            routes.append(path)

        return [Route(path) for path in routes]

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
