import pygame

from src.models.drone import Drone
from src.routing.graph import Graph
from src.simulation.simulation import Simulation

from .render import Renderer


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

        display_info = pygame.display.Info()
        screen_width = display_info.current_w
        screen_height = display_info.current_h

        self.screen = pygame.display.set_mode(
            (screen_width, screen_height),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption("Fly-in")

        self.clock = pygame.time.Clock()

        self.renderer = Renderer(
            self.screen,
            self.graph,
            self.drones,
            self.simulation,
            self.animation_start,
            self.animation_duration,
        )

    def run(self) -> None:
        running = True

        while running:
            running = self._handle_events()

            current_time = pygame.time.get_ticks()

            self._update(current_time)

            self.renderer.draw(
                current_time,
                self.paused,
                self.step_interval,
            )

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE,
                )

                self.renderer.geometry.screen = self.screen

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                elif event.key == pygame.K_LEFT:
                    self.step_interval = min(
                        self.step_interval + 100,
                        3000,
                    )

                elif event.key == pygame.K_RIGHT:
                    self.step_interval = max(
                        self.step_interval - 100,
                        100,
                    )

                elif event.key == pygame.K_h:
                    self.renderer.toggle_hub_info()

                elif event.key == pygame.K_r:
                    self._reset()

        return True

    def _reset(self) -> None:
        self.simulation.reset()

        current_time = pygame.time.get_ticks()
        self.last_step = current_time

        for drone in self.drones:
            self.animation_start[
                drone.drone_id
            ] = current_time

    def _update(self, current_time: int) -> None:
        if self.paused:
            return

        if self.simulation.finished:
            return

        if (
            current_time - self.last_step
            < self.step_interval
        ):
            return

        was_moving = {
            drone.drone_id: drone.moving
            for drone in self.drones
        }

        positions_before = {
            drone.drone_id: drone.current_hub
            for drone in self.drones
        }

        self.simulation.step()
        self.last_step = current_time

        self._update_animations(
            current_time,
            was_moving,
            positions_before,
        )

    def _update_animations(
        self,
        current_time: int,
        was_moving: dict[int, bool],
        positions_before: dict[int, str],
    ) -> None:
        for drone in self.drones:
            drone_id = drone.drone_id
            previous_hub = positions_before[drone_id]
            current_hub = drone.current_hub
            movement_changed = previous_hub != current_hub
            travel_state_changed = was_moving[drone_id] != drone.moving

            if movement_changed or travel_state_changed:
                self.animation_start[drone_id] = current_time
