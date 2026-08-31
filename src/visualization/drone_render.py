import math

import pygame

from src.models.drone import Drone
from src.routing.graph import Graph
from src.simulation.simulation import Simulation


class DroneRenderer:
    def __init__(
        self,
        screen,
        graph: Graph,
        drones: list[Drone],
        simulation: Simulation,
        geometry,
        animation_start: dict[int, int],
        animation_duration: int,
    ) -> None:
        self.screen = screen
        self.graph = graph
        self.drones = drones
        self.simulation = simulation
        self.geometry = geometry
        self.animation_start = animation_start
        self.animation_duration = animation_duration

    def draw(self, current_time: int) -> None:
        grouped: dict[str, list[Drone]] = {}

        for drone in self.drones:
            grouped.setdefault(
                drone.current_hub,
                [],
            ).append(drone)

        for drones in grouped.values():
            for index, drone in enumerate(drones):
                position = self._get_position(
                    drone,
                    current_time,
                )

                position = self.geometry.offset_drone_position(
                    position,
                    index,
                    len(drones),
                )

                angle = self._get_angle(drone)

                self._draw_drone(position, angle)
                self._draw_id(position, drone.drone_id)
                self._draw_progress(
                    drone,
                    position,
                    current_time,
                )

    def _get_position(
        self,
        drone: Drone,
        current_time: int,
    ) -> tuple[int, int]:
        hubs = self.graph.fly_map.hubs

        current_hub = hubs[drone.current_hub]

        previous_name = (
            self.simulation.get_drone_previous_hub(
                drone.drone_id
            )
        )

        previous_hub = hubs[previous_name]
        target_hub = current_hub

        movement_cost = drone.last_move_cost

        if drone.moving:
            target_hub = hubs[
                drone.route.hubs[drone.position + 1]
            ]
            previous_hub = current_hub

        start_time = self.animation_start.get(
            drone.drone_id,
            current_time,
        )

        elapsed = current_time - start_time

        progress = min(
            elapsed
            / (self.animation_duration * movement_cost),
            1.0,
        )

        x = previous_hub.x + (
            target_hub.x - previous_hub.x
        ) * progress

        y = previous_hub.y + (
            target_hub.y - previous_hub.y
        ) * progress

        return self.geometry.position(
            hubs,
            x,
            y,
        )

    def _get_angle(self, drone: Drone) -> float:
        if drone.finished:
            return 0.0

        hubs = self.graph.fly_map.hubs

        current = hubs[drone.current_hub]

        next_hub = hubs[
            drone.route.hubs[drone.position + 1]
        ]

        dx = next_hub.x - current.x
        dy = next_hub.y - current.y

        return math.degrees(
            math.atan2(dy, dx)
        )

    def _draw_drone(
        self,
        position: tuple[int, int],
        angle: float,
    ) -> None:
        x, y = position

        points = [
            (14, 0),
            (-8, -8),
            (-4, 0),
            (-8, 8),
        ]

        radians = math.radians(angle)
        cos_angle = math.cos(radians)
        sin_angle = math.sin(radians)

        rotated_points = []

        for px, py in points:
            rx = px * cos_angle - py * sin_angle
            ry = px * sin_angle + py * cos_angle

            rotated_points.append(
                (
                    round(x + rx),
                    round(y + ry),
                )
            )

        pygame.draw.polygon(
            self.screen,
            (240, 200, 50),
            rotated_points,
        )

    def _draw_id(
        self,
        position: tuple[int, int],
        drone_id: int,
    ) -> None:
        font = pygame.font.Font(None, 16)

        label = font.render(
            str(drone_id),
            True,
            (30, 30, 30),
        )

        self.screen.blit(
            label,
            (
                position[0] - label.get_width() // 2,
                position[1] - label.get_height() // 2,
            ),
        )

    def _draw_progress(
        self,
        drone: Drone,
        position: tuple[int, int],
        current_time: int,
    ) -> None:
        if not drone.moving or drone.last_move_cost != 2:
            return

        start_time = self.animation_start.get(
            drone.drone_id,
            current_time,
        )

        progress = min(
            (current_time - start_time)
            / self.animation_duration,
            1.0,
        )

        rectangle = pygame.Rect(
            position[0] - 27,
            position[1] - 27,
            54,
            54,
        )

        pygame.draw.arc(
            self.screen,
            (255, 235, 80),
            rectangle,
            math.pi / 2,
            math.pi / 2 + math.tau * progress,
            4,
        )

        font = pygame.font.Font(None, 16)

        label = font.render(
            "2T",
            True,
            (255, 235, 80),
        )

        self.screen.blit(
            label,
            (
                position[0] - label.get_width() // 2,
                position[1] + 30,
            ),
        )
