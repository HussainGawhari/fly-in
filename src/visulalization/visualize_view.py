import pygame

from src.models.drone import Drone
from src.routing.graph import Graph


class PygameView:
    def __init__(
        self,
        graph: Graph,
        drones: list[Drone],
    ) -> None:
        self.graph = graph
        self.drones = drones

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
        hubs = self.graph.fly_map.hubs

        for drone in self.drones:
            hub = hubs[drone.current_hub]

            pygame.draw.circle(
                self.screen,
                (240, 200, 50),
                self._position(hub.x, hub.y),
                8,
            )

    def _position(self, x: int, y: int) -> tuple[int, int]:
        scale = 100
        offset_x = 100
        offset_y = 100

        return (
            offset_x + x * scale,
            offset_y + y * scale,
        )
