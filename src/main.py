from pathlib import Path
import sys

from src.exception import ParserError
from src.parser.parser import MapParser
from src.routing.graph import Graph
from src.routing.path_finder import Pathfinder


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m fly_in.main <map_file>")
        return 1

    path = Path(sys.argv[1])

    try:
        fly_map = MapParser().parse_file(path)
    except (OSError, ParserError) as error:
        print(f"Error: {error}")
        return 1

    graph = Graph(fly_map)

    pathfinder = Pathfinder(graph)

    path = pathfinder.find_path(
        fly_map.start_hub,
        fly_map.end_hub,
    )

    if path is None:
        print("No path found")
    else:
        print("Path found:")
        print(" -> ".join(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
