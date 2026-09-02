from pydantic import BaseModel, Field, model_validator


class Hub(BaseModel):
    """Represents a map node with position, zone, and optional capacity rules.

    Hubs can be start, end, priority, blocked, or restricted, and may enforce a
    maximum number of drones allowed to occupy them.
    """

    name: str
    x: int
    y: int

    zone: str = "normal"
    color: str | None = None
    max_drones: int | None = Field(default=1, gt=0)

    is_start: bool = False
    is_end: bool = False

    @model_validator(mode="after")
    def normalize_capacity(self) -> "Hub":
        """Ensure the start and end hubs keep unlimited capacity."""
        if self.is_start or self.is_end:
            self.max_drones = None
        return self
