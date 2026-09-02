import math

import pygame

from src.models.drone import Drone
from src.routing.graph import Graph
from src.simulation.simulation import Simulation
from src.visualization.geometry import Geometry


class DroneRenderer:
    def __init__(
        self,
        screen: pygame.Surface,
        graph: Graph,
        drones: list[Drone],
        simulation: Simulation,
        geometry: Geometry,
        animation_start: dict[int, int],
        animation_duration: int,
    ) -> None:
        self.screen = screen
        self.graph = graph
        self.drones = drones
        self.sim = simulation
        self.geo = geometry
        self.anim_start = animation_start
        self.duration = animation_duration

    def draw(self, time: int) -> None:
        grouped: dict[str, list[Drone]] = {}

        for drone in self.drones:
            grouped.setdefault(
                drone.current_hub,
                [],
            ).append(drone)

        for drones in grouped.values():
            for index, drone in enumerate(drones):
                position = self.geo.offset_drone_position(
                    self._get_position(drone, time),
                    index,
                    len(drones),
                )

                self._draw_drone(
                    position,
                    self._get_angle(drone),
                )

                self._draw_id(
                    position,
                    drone.drone_id,
                )

                self._draw_progress(
                    drone,
                    position,
                    time,
                )

    def _get_position(
        self,
        drone: Drone,
        time: int,
    ) -> tuple[int, int]:
        hubs = self.graph.fly_map.hubs
        current_hub = hubs[drone.current_hub]
        previous_name = (
            self.sim.get_drone_previous_hub(
                drone.drone_id,
            )
        )
        previous_hub = hubs[previous_name]

        if drone.moving:
            source_hub = current_hub
            target_hub = hubs[
                drone.route.hubs[
                    drone.position + 1
                ]
            ]
            movement_cost = drone.last_move_cost
        else:
            source_hub = previous_hub
            target_hub = current_hub
            movement_cost = (
                drone.last_move_cost
                if previous_hub != current_hub
                else 1
            )

        if source_hub == target_hub:
            return self.geo.position(
                hubs,
                current_hub.x,
                current_hub.y,
            )

        start_time = self.anim_start.get(
            drone.drone_id,
            time,
        )

        progress = min(
            (
                time - start_time
            ) / (
                self.duration * movement_cost
            ),
            1.0,
        )

        x = (
            source_hub.x
            + (target_hub.x - source_hub.x)
            * progress
        )

        y = (
            source_hub.y
            + (target_hub.y - source_hub.y)
            * progress
        )

        return self.geo.position(
            hubs,
            x,
            y,
        )

    def _get_angle(
        self,
        drone: Drone,
    ) -> float:
        if drone.finished:
            return 0.0

        hubs = self.graph.fly_map.hubs
        current_hub = hubs[drone.current_hub]
        next_hub = hubs[
            drone.route.hubs[
                drone.position + 1
            ]
        ]

        dx = next_hub.x - current_hub.x
        dy = next_hub.y - current_hub.y

        return math.degrees(
            math.atan2(dy, dx)
        )

    def _draw_drone(
        self,
        position: tuple[int, int],
        angle: float,
    ) -> None:
        x, y = position

        radians = math.radians(angle)
        cos_angle = math.cos(radians)
        sin_angle = math.sin(radians)

        points = [
            (14, 0),
            (-8, -8),
            (-4, 0),
            (-8, 8),
        ]

        rotated_points = [
            (
                round(
                    x + px * cos_angle - py * sin_angle,
                ),
                round(
                    y + px * sin_angle + py * cos_angle,
                ),
            )
            for px, py in points
        ]

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
                position[0]
                - label.get_width() // 2,
                position[1]
                - label.get_height() // 2,
            ),
        )

    def _draw_progress(
        self,
        drone: Drone,
        position: tuple[int, int],
        time: int,
    ) -> None:
        if drone.last_move_cost != 2:
            return

        previous_name = (
            self.sim.get_drone_previous_hub(
                drone.drone_id,
            )
        )

        if (
            not drone.moving
            and previous_name == drone.current_hub
        ):
            return

        start_time = self.anim_start.get(
            drone.drone_id,
            time,
        )

        progress = min(
            (
                time - start_time
            ) / (
                self.duration * 2
            ),
            1.0,
        )

        if progress >= 1.0:
            return

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
            math.pi / 2
            + math.tau * progress,
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
                position[0]
                - label.get_width() // 2,
                position[1] + 30,
            ),
        )
