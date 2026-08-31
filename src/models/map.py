from pydantic import BaseModel, Field

from src.models.hub import Hub
from src.models.connection import Connection


class FlyMap(BaseModel):
    """Container for the parsed map data used by the graph and simulator.

    It stores the drone count, all hubs, the connections between them, and the
    start and end hubs required by the routing logic.
    """

    nb_drones: int = Field(gt=0)

    hubs: dict[str, Hub] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)

    start_hub: str | None = None
    end_hub: str | None = None
