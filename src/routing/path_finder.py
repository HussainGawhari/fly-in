from collections import deque

from src.routing.graph import Graph


class Pathfinder:

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_path(self, start: str, goal: str) -> list[str] | None:
        queue: deque[str] = deque()
        queue.append(start)

        visited: set[str] = set()
        visited.add(start)
        parent: dict[str, str | None] = {}
        parent[start] = None

        while queue:
            current = queue.popleft()

            if current == goal:
                return self._build_path(parent, goal)
            for neighbor in self.graph.neighbors(current):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
        return None

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
