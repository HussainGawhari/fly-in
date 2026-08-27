import heapq

from src.models.route import Route
from src.routing.graph import Graph


class Pathfinder:

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_path(self, start: str, goal: str) -> list[str] | None:
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

        paths: list[Route] = []
        current_path: list[str] = [start]
        visited_path: set[str] = {start}

        self._find_paths(
            current=start,
            goal=goal,
            current_path=current_path,
            visited=visited_path,
            paths=paths,
            max_paths=max_paths,
        )

        return paths

    def _find_paths(
        self,
        current: str,
        goal: str,
        current_path: list[str],
        visited: set[str],
        paths: list[Route],
        max_paths: int,
    ) -> None:
        if len(paths) >= max_paths:
            return

        if current == goal:
            paths.append(Route(current_path.copy()))
            return

        for neighbor in self.graph.neighbors(current):
            if self.graph.fly_map.hubs[neighbor].zone == "blocked":
                continue
            if neighbor in visited:
                continue

            visited.add(neighbor)
            current_path.append(neighbor)

            self._find_paths(
                current=neighbor,
                goal=goal,
                current_path=current_path,
                visited=visited,
                paths=paths,
                max_paths=max_paths,
            )

            current_path.pop()
            visited.remove(neighbor)

    def _build_path(
        self,
        parent: dict[str, str | None],
        goal: str,
    ) -> list[str]:
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
        paths = self.find_paths(start, goal, max_paths)
        paths.sort(key=self._route_cost)

        return paths

    def _movement_cost(self, hub_name: str) -> int:
        zone = self.graph.fly_map.hubs[hub_name].zone
        return 2 if zone == "restricted" else 1

    def _priority_penalty(self, hub_name: str) -> int:
        return 0 if self.graph.fly_map.hubs[hub_name].zone == "priority" else 1

    def _route_cost(self, route: Route) -> tuple[int, int]:
        return (
            sum(self._movement_cost(hub) for hub in route.hubs[1:]),
            sum(self._priority_penalty(hub) for hub in route.hubs[1:]),
        )
