from collections import deque

from src.models.route import Route
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
    ) -> list[list[str]]:
        paths = self.find_paths(start, goal, max_paths)

        paths.sort(key=len)

        return paths
