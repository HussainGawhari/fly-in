from pydantic import BaseModel, Field

from src.models.hub import Hub
from src.models.connection import Connection


class FlyMap(BaseModel):
    nb_drones: int = Field(gt=0)

    hubs: dict[str, Hub] = {}
    connections: list[Connection] = []
    start_hub: str | None = None
    end_hub: str | None = None
