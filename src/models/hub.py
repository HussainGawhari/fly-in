from pydantic import BaseModel, Field, model_validator


"""
    This class represend the following output
    hub: bottleneck 1 0 [color=orange max_drones=2]
"""


class Hub(BaseModel):
    name: str
    x: int
    y: int

    zone: str = "normal"
    color: str | None = None
    max_drones: int | None = Field(default=1, gt=0)

    is_start: bool = False
    is_end: bool = False

    @model_validator(mode="after")
    def normalize_capacity(self):
        if self.is_start or self.is_end:
            self.max_drones = None
        return self
