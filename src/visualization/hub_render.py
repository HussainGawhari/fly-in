import pygame

from src.models.drone import Drone
from src.models.hub import Hub
from src.routing.graph import Graph
from src.visualization.geometry import Geometry


class HubRenderer:
    """Draws hubs and their metadata, such as names and current occupancy."""

    COLORS: dict[str, tuple[int, int, int]] = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "brown": (139, 69, 19),
        "maroon": (128, 0, 0),
        "gold": (255, 215, 0),
        "darkred": (139, 0, 0),
        "violet": (238, 130, 238),
        "crimson": (220, 20, 60),
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "gray": (128, 128, 128),
        "grey": (128, 128, 128),
    }

    def __init__(
        self,
        screen: pygame.Surface,
        graph: Graph,
        drones: list[Drone],
        geometry: Geometry,
    ) -> None:
        self.screen = screen
        self.graph = graph
        self.drones = drones
        self.geometry = geometry
        self.show_hub_info = False

    def toggle_hub_info(self) -> None:
        self.show_hub_info = not self.show_hub_info

    def draw(self) -> None:
        font = pygame.font.Font(None, 24)

        for hub in self.graph.fly_map.hubs.values():
            position = self.geometry.position(
                self.graph.fly_map.hubs,
                hub.x,
                hub.y,
            )

            pygame.draw.circle(
                self.screen,
                self._color(hub),
                position,
                26,
            )

            if hub.zone == "restricted":
                pygame.draw.circle(
                    self.screen,
                    (100, 190, 255),
                    position,
                    33,
                    3,
                )

            if self.show_hub_info:
                label = font.render(
                    hub.name,
                    True,
                    (255, 255, 255),
                )

                self.screen.blit(
                    label,
                    (
                        position[0] - label.get_width() // 2,
                        position[1] - 45,
                    ),
                )
            if self.show_hub_info:
                self._draw_capacity(
                    hub,
                    position,
                    font,
                )

    def _draw_capacity(
        self,
        hub: Hub,
        position: tuple[int, int],
        font: pygame.font.Font,
    ) -> None:
        usage = sum(
            drone.current_hub == hub.name
            for drone in self.drones
        )

        if hub.max_drones is not None:
            text = f"{usage}/{hub.max_drones}"
        else:
            text = str(usage)

        label = font.render(
            text,
            True,
            (220, 220, 220),
        )

        self.screen.blit(
            label,
            (
                position[0] - label.get_width() // 2,
                position[1] + 25,
            ),
        )

    def _color(self, hub: Hub) -> tuple[int, int, int]:
        if hub.color is not None:
            return self.COLORS.get(
                hub.color.lower(),
                (90, 140, 200),
            )

        if hub.is_start:
            return (50, 200, 80)

        if hub.is_end:
            return (220, 60, 60)

        if hub.zone == "blocked":
            return (60, 60, 60)

        if hub.zone == "restricted":
            return (60, 120, 220)

        if hub.zone == "priority":
            return (240, 160, 40)

        return (90, 140, 200)
