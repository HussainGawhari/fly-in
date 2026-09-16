from pathlib import Path
import sys

from src.exception import ParserError
from src.parser.parser import MapParser
from src.graph.graph import Graph
from src.graph.algorithms import Pathfinder
from src.simulation.scheduler import Scheduler
from src.simulation.simulation import Simulation
from src.visualization.pygame_view import PygameView


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m src.main <map_file>")
        return 1

    map_path = Path(sys.argv[1])
    if not map_path.is_file():
        print(f"Error: '{map_path}' is not a valid file.")
        return 1

    try:
        fly_map = MapParser().parse_file(map_path)
    except (OSError, ParserError) as error:
        print(f"Error: {error}")
        return 1

    graph = Graph(fly_map)
    routes = Pathfinder(graph).find_best_paths(
        fly_map.start_hub,
        fly_map.end_hub)
    if not routes:
        print("No solution found for this map")
        return 1

    drones = Scheduler(routes, fly_map.nb_drones).create_drones()
    if not drones:
        print("No solution found for this map")
        return 1

    simulation = Simulation(drones, graph)

    try:
        PygameView(graph, drones, simulation).run()
    except KeyboardInterrupt:
        print("\nSimulation closed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
