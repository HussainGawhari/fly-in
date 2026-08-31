from dataclasses import dataclass


@dataclass
class Route:
    """Stores the ordered hub sequence that a drone must follow.

    A route is a simple path description; its length is the number of links it
    crosses between the first and last hub.
    """

    hubs: list[str]

    @property
    def length(self) -> int:
        """Return the number of travel steps in the route."""
        return len(self.hubs) - 1
