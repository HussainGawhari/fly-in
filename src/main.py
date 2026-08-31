from pathlib import Path
import sys

from src.exception import ParserError
from src.parser.parser import MapParser
from src.routing.graph import Graph
from src.routing.path_finder import Pathfinder
from src.simulation.scheduler import Scheduler
from src.simulation.simulation import Simulation
from src.visualization.pygame_view import PygameView


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m src.main <map_file>")
        return 1

    map_path = Path(sys.argv[1])

    try:
        fly_map = MapParser().parse_file(map_path)
    except (OSError, ParserError) as error:
        print(f"Error: {error}")
        return 1

    if fly_map.start_hub is None or fly_map.end_hub is None:
        print("Error: start_hub or end_hub is missing")
        return 1

    graph = Graph(fly_map)
    pathfinder = Pathfinder(graph)

    routes = pathfinder.find_best_paths(
        fly_map.start_hub,
        fly_map.end_hub,
    )

    if not routes:
        print("No path found")
        return 1

    for index, route in enumerate(routes, start=1):
        print(f"{index}: {' -> '.join(route.hubs)}")

    scheduler = Scheduler(routes, fly_map.nb_drones)
    drones = scheduler.create_drones()

    #print("\nDrone assignments:")
    #for drone in drones:
    #    print(
    #        f"Drone {drone.drone_id}: "
    #        f"{' -> '.join(drone.route.hubs)}"
    #    )

    simulation = Simulation(drones, graph)

    view = PygameView(
        graph,
        drones,
        simulation,
    )

    view.run()

    print("\n" + "=" * 50)
    print("SIMULATION SOLUTION")
    print("=" * 50)
    print(f"Total turns: {simulation.time}")
    print(f"Total drones: {len(drones)}")

    #print("\nFinal routes:")
    #for drone in drones:
    #    print(
    #        f"Drone {drone.drone_id}: "
    #        f"{' -> '.join(drone.route.hubs)}"
    #    )

    #print("\nFinal positions:")
    #for drone in drones:
    #    print(
    #        f"Drone {drone.drone_id}: "
    #        f"{drone.current_hub}"
    #    )

    #print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
