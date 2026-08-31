from pydantic import BaseModel, Field


class Connection(BaseModel):
    """Represents a bidirectional link between two hubs.

    The link keeps a maximum flow value so the simulation can enforce traffic
    constraints during route execution.
    """

    hub1: str
    hub2: str
    max_link_capacity: int = Field(default=1, gt=0)

    @property
    def key(self) -> frozenset[str]:
        """Return a canonical key for a connection.

        This ensures A-B and B-A are treated as the same link.
        """
        return frozenset((self.hub1, self.hub2))
