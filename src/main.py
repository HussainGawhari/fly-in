from pathlib import Path
import sys

from src.exception import ParserError
from src.parser.parser import MapParser
from src.routing.graph import Graph


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

    # print(f"Drones: {fly_map.nb_drones}")
    # print(f"Hubs: {len(fly_map.hubs)}")
    # print(f"Connections: {len(fly_map.connections)}")

    # print("Start:", fly_map.start_hub)
    # print("Goal:", fly_map.end_hub)

    # path = Path("maps/easy/02_simple_fork.txt")

    # fly_map = MapParser().parse_file(path)

    graph = Graph(fly_map)

    print("Start:", fly_map.start_hub)
    print("Goal:", fly_map.end_hub)
    print(fly_map.connections)

    # print("Neighbors of start:", graph.neighbors("start"))
    # print("Neighbors of junction:", graph.neighbors("waypoint1"))
    # print("Neighbors of path_a:", graph.neighbors("waypoint2"))
    # print("Neighbors of goal:", graph.neighbors("goal"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
