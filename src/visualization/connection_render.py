import pygame

from src.routing.graph import Graph


class ConnectionRenderer:
    def __init__(self, screen, graph: Graph, geometry) -> None:
        self.screen = screen
        self.graph = graph
        self.geometry = geometry

    def draw(self) -> None:
        font = pygame.font.Font(None, 18)
        hubs = self.graph.fly_map.hubs

        for connection in self.graph.fly_map.connections:
            hub1 = hubs[connection.hub1]
            hub2 = hubs[connection.hub2]

            start = self.geometry.position(
                hubs,
                hub1.x,
                hub1.y,
            )

            end = self.geometry.position(
                hubs,
                hub2.x,
                hub2.y,
            )

            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                start,
                end,
                3,
            )

            middle = (
                (start[0] + end[0]) // 2,
                (start[1] + end[1]) // 2,
            )

            label = font.render(
                str(connection.max_link_capacity),
                True,
                (180, 180, 180),
            )

            self.screen.blit(label, middle)
