import unittest
from io import StringIO
from contextlib import redirect_stdout

from src.models.drone import Drone
from src.models.route import Route
from src.simulation.simulation import Simulation


class DummyHub:
    def __init__(self, name: str, zone: str = "normal", max_drones: int | None = None):
        self.name = name
        self.zone = zone
        self.max_drones = max_drones


class DummyConnection:
    def __init__(self, hub1: str, hub2: str):
        self.hub1 = hub1
        self.hub2 = hub2
        self.key = frozenset((hub1, hub2))
        self.max_link_capacity = 1


class DummyGraph:
    def __init__(self, hubs=None, connections=None):
        self.fly_map = type(
            "Map",
            (),
            {
                "hubs": hubs or {},
                "connections": connections or [],
            },
        )()


class SimulationOutputTest(unittest.TestCase):
    def test_simulation_prints_location_for_stationary_drones(self):
        graph = DummyGraph(
            hubs={
                "start": DummyHub("start"),
                "goal": DummyHub("goal"),
            }
        )
        drones = [
            Drone(1, Route(["start", "goal"])),
            Drone(2, Route(["start", "goal"])),
        ]
        simulation = Simulation(drones, graph)

        with redirect_stdout(StringIO()) as stdout:
            simulation._print_state()
            output = stdout.getvalue()

        self.assertEqual(output, "D1-start D2-start\n")

    def test_simulation_prints_connection_name_for_restricted_zone_travel(self):
        graph = DummyGraph(
            hubs={
                "start": DummyHub("start"),
                "restricted": DummyHub("restricted", zone="restricted"),
            },
            connections=[DummyConnection("start", "restricted")],
        )
        drone = Drone(1, Route(["start", "restricted"]))
        drone.travel_remaining = 1
        simulation = Simulation([drone], graph)

        with redirect_stdout(StringIO()) as stdout:
            simulation._print_state()
            output = stdout.getvalue()

        self.assertEqual(output, "D1-start-restricted\n")


if __name__ == "__main__":
    unittest.main()
