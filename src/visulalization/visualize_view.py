import pygame

from src.models.drone import Drone
from src.routing.graph import Graph
from src.simulation.simulation import Simulation


class PygameView:
    def __init__(
        self,
        graph: Graph,
        drones: list[Drone],
        simulation: Simulation,
    ) -> None:
        self.graph = graph
        self.drones = drones
        self.simulation = simulation

        self.step_interval = 1000
        self.animation_duration = 500
        self.last_step = pygame.time.get_ticks()

        self.animation_start: dict[int, int] = {}

        pygame.init()

        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("Fly-in")

        self.clock = pygame.time.Clock()

    def run(self) -> None:
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            current_time = pygame.time.get_ticks()

            if (
                not self.simulation.finished
                and current_time - self.last_step >= self.step_interval
            ):
                self.simulation.step()
                self.last_step = current_time

                for drone in self.drones:
                    self.animation_start[drone.drone_id] = current_time

            self.screen.fill((30, 30, 30))

            self._draw_connections()
            self._draw_hubs()
            self._draw_drones()

            pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()

    def _draw_connections(self) -> None:
        hubs = self.graph.fly_map.hubs

        for connection in self.graph.fly_map.connections:
            hub1 = hubs[connection.hub1]
            hub2 = hubs[connection.hub2]

            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                self._position(hub1.x, hub1.y),
                self._position(hub2.x, hub2.y),
                3,
            )

    def _draw_hubs(self) -> None:
        for hub in self.graph.fly_map.hubs.values():
            position = self._position(hub.x, hub.y)

            pygame.draw.circle(
                self.screen,
                (70, 150, 220),
                position,
                20,
            )

    def _draw_drones(self) -> None:
        current_time = pygame.time.get_ticks()

        for drone in self.drones:
            position = self._get_drone_position(
                drone,
                current_time,
            )

            pygame.draw.circle(
                self.screen,
                (240, 200, 50),
                position,
                8,
            )

    def _get_drone_position(
        self,
        drone: Drone,
        current_time: int,
    ) -> tuple[int, int]:
        current_hub = self.graph.fly_map.hubs[drone.current_hub]

        previous_name = self.simulation.get_drone_previous_hub(
            drone.drone_id
        )

        previous_hub = self.graph.fly_map.hubs[previous_name]

        start_time = self.animation_start.get(
            drone.drone_id,
            current_time,
        )

        elapsed = current_time - start_time

        progress = min(
            elapsed / self.animation_duration,
            1.0,
        )

        x = previous_hub.x + (
            current_hub.x - previous_hub.x
        ) * progress

        y = previous_hub.y + (
            current_hub.y - previous_hub.y
        ) * progress

        return self._position(x, y)

    def _position(
        self,
        x: float,
        y: float,
    ) -> tuple[int, int]:
        scale = 100
        offset_x = 100
        offset_y = 100

        return (
            round(offset_x + x * scale),
            round(offset_y + y * scale),
        )
