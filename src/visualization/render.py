from src.models.drone import Drone
from src.routing.graph import Graph
from src.simulation.simulation import Simulation

from .connection_render import ConnectionRenderer
from .control_render import ControlsRenderer
from .drone_render import DroneRenderer
from .geometry import Geometry
from .hub_render import HubRenderer


class Renderer:
    def __init__(
        self,
        screen,
        graph: Graph,
        drones: list[Drone],
        simulation: Simulation,
        animation_start: dict[int, int],
        animation_duration: int,
    ) -> None:
        self.screen = screen

        self.geometry = Geometry(screen)

        self.connections = ConnectionRenderer(
            screen,
            graph,
            self.geometry,
        )

        self.hubs = HubRenderer(
            screen,
            graph,
            drones,
            self.geometry,
        )

        self.drones = DroneRenderer(
            screen,
            graph,
            drones,
            simulation,
            self.geometry,
            animation_start,
            animation_duration,
        )

        self.controls = ControlsRenderer(
            screen,
            drones,
            simulation,
        )

    def draw(
        self,
        current_time: int,
        paused: bool,
        step_interval: int,
    ) -> None:
        self.screen.fill((30, 30, 30))

        self.connections.draw()
        self.hubs.draw()
        self.drones.draw(current_time)

        self.controls.draw(
            paused,
            step_interval,
        )

        self.controls.draw_info()
