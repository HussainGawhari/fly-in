import pygame
import math

from src.models.drone import Drone
from src.models.hub import Hub
from src.routing.graph import Graph
from src.simulation.simulation import Simulation


class PygameView:

    def __init__(
        self,
        graph: Graph,
        drones: list[Drone],
        simulation: Simulation,
    ) -> None:
        pygame.init()

        self.graph = graph
        self.drones = drones
        self.simulation = simulation

        self.step_interval = 1000
        self.animation_duration = 500
        self.last_step = pygame.time.get_ticks()

        self.paused = False
        self.animation_start: dict[int, int] = {}

        self.screen = pygame.display.set_mode(
            (1000, 700),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption("Fly-in")

        self.clock = pygame.time.Clock()

    def run(self) -> None:
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h),
                        pygame.RESIZABLE,
                    )

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused

                    elif event.key == pygame.K_r:
                        self.simulation.reset()
                        current_time = pygame.time.get_ticks()
                        self.last_step = current_time

                        for drone in self.drones:
                            self.animation_start[drone.drone_id] = current_time

            current_time = pygame.time.get_ticks()

            if (
                not self.paused
                and not self.simulation.finished
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
            self._draw_controls()
            pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()

    def _draw_connections(self) -> None:
        font = pygame.font.Font(None, 18)
        hubs = self.graph.fly_map.hubs

        for connection in self.graph.fly_map.connections:
            hub1 = hubs[connection.hub1]
            hub2 = hubs[connection.hub2]

            start = self._position(hub1.x, hub1.y)
            end = self._position(hub2.x, hub2.y)

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

            self.screen.blit(
                label,
                middle,
            )

    def _draw_hubs(self) -> None:
        font = pygame.font.Font(None, 24)

        for hub in self.graph.fly_map.hubs.values():
            position = self._position(hub.x, hub.y)

            color = self._hub_color(hub)

            pygame.draw.circle(
                self.screen,
                color,
                position,
                22,
            )

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

            self._draw_capacity(
                hub.name,
                position,
                font,
            )

    def _draw_drones(self) -> None:
        current_time = pygame.time.get_ticks()

        grouped: dict[str, list[Drone]] = {}

        for drone in self.drones:
            grouped.setdefault(drone.current_hub, []).append(drone)

        for drones in grouped.values():
            for index, drone in enumerate(drones):
                position = self._get_drone_position(
                    drone,
                    current_time,
                )

                position = self._offset_drone_position(
                    position,
                    index,
                    len(drones),
                )

                angle = self._get_drone_angle(drone)

                self._draw_drone(position, angle)

    def _offset_drone_position(
        self,
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

        rotated_points: list[tuple[int, int]] = []

        radians = math.radians(angle)

        cos_angle = math.cos(radians)
        sin_angle = math.sin(radians)

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
        hubs = list(self.graph.fly_map.hubs.values())

        min_x = min(hub.x for hub in hubs)
        max_x = max(hub.x for hub in hubs)
        min_y = min(hub.y for hub in hubs)
        max_y = max(hub.y for hub in hubs)

        map_width = max_x - min_x
        map_height = max_y - min_y

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
            window_height - control_height - rendered_height
        ) / 2

        screen_x = offset_x + (x - min_x) * scale
        screen_y = offset_y + (y - min_y) * scale

        return round(screen_x), round(screen_y)

    #def _hub_color(self, hub: Hub) -> tuple[int, int, int]:
    #    if hub.color is not None:
    #        color = pygame.Color(hub.color)
    #        return (color.r, color.g, color.b)

    #    if hub.is_start:
    #        return (50, 200, 80)

    #    if hub.is_end:
    #        return (220, 60, 60)

    #    if hub.zone == "blocked":
    #        return (60, 60, 60)

    #    if hub.zone == "restricted":
    #        return (60, 120, 220)

    #    if hub.zone == "priority":
    #        return (240, 160, 40)

    #    return (90, 140, 200)

    def _hub_color(self, hub: Hub) -> tuple[int, int, int]:
        colors: dict[str, tuple[int, int, int]] = {
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

        if hub.color is not None:
            return colors.get(
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

    def _draw_capacity(
        self,
        hub_name: str,
        position: tuple[int, int],
        font: pygame.font.Font,
    ) -> None:
        usage = sum(
            1
            for drone in self.drones
            if drone.current_hub == hub_name
        )

        hub = self.graph.fly_map.hubs[hub_name]

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

    def _draw_controls(self) -> None:
        font = pygame.font.Font(None, 24)

        if self.paused:
            status = "PAUSED"
        elif self.simulation.finished:
            status = "FINISHED"
        else:
            status = "RUNNING"

        text = (
            f"{status} | "
            f"Time: {self.simulation.time} | "
            f"Speed: {1000 / self.step_interval:.1f} steps/s | "
            f"SPACE: pause | +/-: speed | R: restart | ESC: quit"
        )

        label = font.render(
            text,
            True,
            (230, 230, 230),
        )

        self.screen.blit(
            label,
            (20, 660),
        )

    def _get_drone_angle(self, drone: Drone) -> float:
        if drone.finished:
            return 0.0

        current = self.graph.fly_map.hubs[
            drone.current_hub
        ]

        next_hub = self.graph.fly_map.hubs[
            drone.route.hubs[drone.position + 1]
        ]

        dx = next_hub.x - current.x
        dy = next_hub.y - current.y

        return math.degrees(
            math.atan2(dy, dx)
        )
