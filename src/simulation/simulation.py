from src.models.drone import Drone


class Simulation:
    def __init__(self, drones: list[Drone]) -> None:
        self.drones = drones
        self.time = 0

    def run(self) -> None:
        while not self._finished():
            self._step()

    def _step(self) -> None:
        self.time += 1

        for drone in self.drones:
            if not drone.finished:
                drone.move()

        self._print_state()

    def _finished(self) -> bool:
        return all(drone.finished for drone in self.drones)

    def _print_state(self) -> None:
        for drone in self.drones:
            print(
                f"{self.time}: "
                f"Drone {drone.drone_id} "
                f"at {drone.current_hub}"
            )
