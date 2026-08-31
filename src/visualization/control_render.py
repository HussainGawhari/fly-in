import pygame

from src.models.drone import Drone
from src.simulation.simulation import Simulation


class ControlsRenderer:
    def __init__(
        self,
        screen,
        drones: list[Drone],
        simulation: Simulation,
    ) -> None:
        self.screen = screen
        self.drones = drones
        self.simulation = simulation

    def draw(
        self,
        paused: bool,
        step_interval: int,
    ) -> None:
        font = pygame.font.Font(None, 24)

        if paused:
            status = "PAUSED"
        elif self.simulation.finished:
            status = "FINISHED"
        else:
            status = "RUNNING"

        text = (
            f"{status} | "
            f"Time: {self.simulation.time} | "
            f"Speed: {1000 / step_interval:.1f} steps/s | "
            f"SPACE: pause | LEFT/RIGHT: speed | "
            f"R: restart | H: hide / unhide info | ESC: quit"
        )

        label = font.render(
            text,
            True,
            (230, 230, 230),
        )

        bottom_y = self.screen.get_height() - 40
        self.screen.blit(label, (20, bottom_y))

    def draw_info(self) -> None:
        font = pygame.font.Font(None, 32)

        finished = sum(
            drone.finished
            for drone in self.drones
        )

        text = font.render(
            (
                f"Turn: {self.simulation.time}   "
                f"Finished: {finished}/{len(self.drones)}"
            ),
            True,
            (255, 255, 255),
        )

        self.screen.blit(text, (20, 20))
