import unittest

from src.models.connection import Connection
from src.models.drone import Drone
from src.models.hub import Hub
from src.models.map import FlyMap
from src.models.route import Route
from src.routing.graph import Graph
from src.routing.path_finder import Pathfinder
from src.simulation.simulation import Simulation


def make_graph(
    hubs: list[Hub],
    connections: list[Connection],
) -> Graph:
    fly_map = FlyMap(
        nb_drones=1,
        hubs={hub.name: hub for hub in hubs},
        connections=connections,
        start_hub="start",
        end_hub="end",
    )
    return Graph(fly_map)


class ConstraintTests(unittest.TestCase):
    def test_zone_capacity_blocks_second_drone(self) -> None:
        graph = make_graph(
            [
                Hub(name="start", x=0, y=0, is_start=True, max_drones=None),
                Hub(name="zone", x=1, y=0),
                Hub(name="end", x=2, y=0, is_end=True, max_drones=None),
            ],
            [
                Connection(hub1="start", hub2="zone"),
                Connection(hub1="zone", hub2="end"),
            ],
        )
        drones = [
            Drone(index, Route(["start", "zone", "end"]))
            for index in (1, 2)
        ]
        simulation = Simulation(drones, graph)

        simulation.step()

        self.assertEqual(
            [drone.current_hub for drone in drones],
            ["zone", "start"],
        )

    def test_restricted_zone_takes_two_turns(self) -> None:
        graph = make_graph(
            [
                Hub(name="start", x=0, y=0, is_start=True, max_drones=None),
                Hub(name="slow", x=1, y=0, zone="restricted"),
                Hub(name="end", x=2, y=0, is_end=True, max_drones=None),
            ],
            [
                Connection(hub1="start", hub2="slow"),
                Connection(hub1="slow", hub2="end"),
            ],
        )
        drone = Drone(1, Route(["start", "slow", "end"]))
        simulation = Simulation([drone], graph)

        simulation.step()
        self.assertEqual(drone.current_hub, "start")
        simulation.step()
        self.assertEqual(drone.current_hub, "start")
        simulation.step()
        self.assertEqual(drone.current_hub, "slow")
        simulation.step()
        self.assertEqual(drone.current_hub, "end")

    def test_pathfinder_skips_blocked_and_prefers_priority(self) -> None:
        graph = make_graph(
            [
                Hub(name="start", x=0, y=0, is_start=True, max_drones=None),
                Hub(name="blocked", x=1, y=0, zone="blocked"),
                Hub(name="normal", x=1, y=1),
                Hub(name="priority", x=1, y=2, zone="priority"),
                Hub(name="end", x=2, y=0, is_end=True, max_drones=None),
            ],
            [
                Connection(hub1="start", hub2="blocked"),
                Connection(hub1="blocked", hub2="end"),
                Connection(hub1="start", hub2="normal"),
                Connection(hub1="normal", hub2="end"),
                Connection(hub1="start", hub2="priority"),
                Connection(hub1="priority", hub2="end"),
            ],
        )

        path = Pathfinder(graph).find_path("start", "end")

        self.assertEqual(path, ["start", "priority", "end"])

    def test_connection_capacity_allows_parallel_moves(self) -> None:
        graph = make_graph(
            [
                Hub(name="start", x=0, y=0, is_start=True, max_drones=None),
                Hub(name="end", x=1, y=0, is_end=True, max_drones=None),
            ],
            [Connection(
                hub1="start",
                hub2="end",
                max_link_capacity=2,
            )],
        )
        drones = [Drone(index, Route(["start", "end"])) for index in (1, 2)]

        Simulation(drones, graph).step()

        self.assertTrue(all(drone.finished for drone in drones))

    def test_connection_default_capacity_blocks_parallel_moves(self) -> None:
        graph = make_graph(
            [
                Hub(name="start", x=0, y=0, is_start=True, max_drones=None),
                Hub(name="end", x=1, y=0, is_end=True, max_drones=None),
            ],
            [Connection(hub1="start", hub2="end")],
        )
        drones = [Drone(index, Route(["start", "end"])) for index in (1, 2)]

        Simulation(drones, graph).step()

        self.assertTrue(drones[0].finished)
        self.assertFalse(drones[1].finished)


if __name__ == "__main__":
    unittest.main()
