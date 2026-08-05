from pydantic import BaseModel, Field


class Connection(BaseModel):
    hub1: str
    hub2: str
    max_link_capacity: int | None = Field(default=1, gt=0)

    """
    Inorder to make A-B and B-A are dublicate
    """
    @property
    def key(self) -> frozenset[str]:
        return frozenset((self.hub1, self.hub2))
