from pathlib import Path
import sys

from src.exception import ParserError
from src.parser.parser import MapParser


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

    print(f"Drones: {fly_map.nb_drones}")
    print(f"Hubs: {len(fly_map.hubs)}")
    print(f"Connections: {len(fly_map.connections)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
