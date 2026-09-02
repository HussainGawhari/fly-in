from __future__ import annotations

import pygame
from src.models.hub import Hub


class Geometry:
    """Handle map scaling and screen coordinates.

    This class converts logical hub positions into pixel coordinates used by
    the Pygame view.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        """Store the current display for conversion."""
        self.screen = screen

    def position(
        self,
        hubs: dict[str, Hub],
        x: float,
        y: float,
    ) -> tuple[int, int]:
        """Map logical coordinates to the current on-screen positions."""
        hub_values = list(hubs.values())

        min_x = min(hub.x for hub in hub_values)
        max_x = max(hub.x for hub in hub_values)
        min_y = min(hub.y for hub in hub_values)
        max_y = max(hub.y for hub in hub_values)

        map_width: int = max_x - min_x
        map_height: int = max_y - min_y

        window_width, window_height = self.screen.get_size()

        padding = 100
        control_height = 50

        available_width = max(
            window_width - padding * 2,
            1,
        )

        available_height = max(
            window_height - padding * 2 - control_height,
            1,
        )

        scale_x = available_width / max(map_width, 1)
        scale_y = available_height / max(map_height, 1)

        scale = min(scale_x, scale_y)

        rendered_width = map_width * scale
        rendered_height = map_height * scale

        offset_x = (
            window_width - rendered_width
        ) / 2

        offset_y = (
            window_height
            - control_height
            - rendered_height
        ) / 2

        screen_x = offset_x + (x - min_x) * scale
        screen_y = offset_y + (y - min_y) * scale

        return round(screen_x), round(screen_y)

    @staticmethod
    def offset_drone_position(
        position: tuple[int, int],
        index: int,
        count: int,
    ) -> tuple[int, int]:
        if count == 1:
            return position

        x, y = position
        spacing = 18

        offsets = [
            (-spacing, 0),
            (spacing, 0),
            (0, -spacing),
            (0, spacing),
            (-spacing, -spacing),
            (spacing, spacing),
        ]

        if index < len(offsets):
            offset_x, offset_y = offsets[index]
            return x + offset_x, y + offset_y

        return x, y
