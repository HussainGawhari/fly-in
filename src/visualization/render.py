import pygame

from src.models.drone import Drone
from src.graph.graph import Graph
from src.simulation.simulation import Simulation

from .connection_render import ConnectionRenderer
from .control_render import ControlsRenderer
from .drone_render import DroneRenderer
from .geometry import Geometry
from .hub_render import HubRenderer


class Renderer:
    """Coordinates all sub-renderers used to draw the simulation view."""

    def __init__(
        self,
        screen: pygame.Surface,
        graph: Graph,
        drones: list[Drone],
        simulation: Simulation,
        animation_start: dict[int, int],
        animation_duration: int,
    ) -> None:
        """Initialize the map, drone, and control renderers for one screen."""
        self.screen = screen
        self.geometry = Geometry(self.screen)

        self.connections = ConnectionRenderer(
            self.screen,
            graph,
            self.geometry,
        )

        self.hubs = HubRenderer(
            self.screen,
            graph,
            drones,
            self.geometry,
        )

        self.drones = DroneRenderer(
            self.screen,
            graph,
            drones,
            simulation,
            self.geometry,
            animation_start,
            animation_duration,
        )

        self.controls = ControlsRenderer(
            self.screen,
            drones,
            simulation,
        )

    def toggle_hub_info(self) -> None:
        self.hubs.toggle_hub_info()
        self.connections.toggle_hub_info()

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
