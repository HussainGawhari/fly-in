from pydantic import Field, BaseModel


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
    max_drones: int | None = Field(default=None, gt=0)

    is_start: bool = False
    is_end: bool = False
