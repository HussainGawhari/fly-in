from src.exception import ParserError
from src.models.connection import Connection
from src.parser.metadata_parser import MetadataParser


class ConnectionParser:
    """Parses a connection declaration from a map file."""

    def __init__(self) -> None:
        """Create the metadata parser used for optional link attributes."""
        self.metadata_parser = MetadataParser()

    def parse(self, content: str, line_number: int) -> Connection:
        """Build a Connection object from a raw connection line."""
        metadata_text = ""

        if "[" in content:
            parts = content.split("[", 1)
            content = parts[0].strip()
            metadata_text = "[" + parts[1]

        if content.count("-") != 1:
            raise ParserError(
                "invalid connection syntax",
                line_number,
            )
        hub1, hub2 = content.split("-")
        hub1 = hub1.strip()
        hub2 = hub2.strip()

        if not hub1 or not hub2:
            raise ParserError(
                "connection required two hubs",
                line_number,
            )
        metadata = self.metadata_parser.parse(
            metadata_text,
            line_number,
        )

        max_capacity = 1

        if "max_link_capacity" in metadata:
            try:
                max_capacity = int(
                    metadata["max_link_capacity"]
                )
            except ValueError:
                raise ParserError(
                    "max_link_capacity must be an integer",
                    line_number,
                )

            if max_capacity <= 0:
                raise ParserError(
                    "max_link_capacity must be positive",
                    line_number,
                )

        return Connection(
            hub1=hub1,
            hub2=hub2,
            max_link_capacity=max_capacity,
        )
