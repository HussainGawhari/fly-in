import pygame

from src.graph.graph import Graph
from src.visualization.geometry import Geometry


class ConnectionRenderer:
    """Draw links and optional capacity labels.

    This renderer is responsible for the visual connection layer in the map.
    """

    def __init__(
            self,
            screen: pygame.Surface,
            graph: Graph,
            geometry: Geometry
            ) -> None:
        """Store the display and geometry used when drawing links."""
        self.screen = screen
        self.graph = graph
        self.geometry = geometry
        self.show_hub_info = True

    def toggle_hub_info(self) -> None:
        """Toggle visibility of link labels and related metadata."""
        self.show_hub_info = not self.show_hub_info

    def draw(self) -> None:
        """Render each connection line and its capacity label.

        Labels are skipped when the visibility toggle is disabled.
        """
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

            if not self.show_hub_info:
                continue

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
