from src.exception import ParserError
from src.models.hub import Hub
from src.parser.metadata_parser import MetadataParser


class HubParser:
    """Parses hub declarations and optional metadata.

    This includes zone information, capacity rules, and start/end markers.
    """

    VALID_ZONES = {
        "normal",
        "blocked",
        "restricted",
        "priority",
    }

    def __init__(self) -> None:
        """Initialize the metadata parser used to read hub attributes."""
        self.metadata_parser = MetadataParser()

    def parse(
            self,
            content: str,
            line_number: int,
            is_start: bool = False,
            is_end: bool = False,
    ) -> Hub:
        """Build a Hub object from a raw line in the map file."""
        metadata_text = ""

        if "[" in content:
            parts = content.split("[", 1)
            if len(parts) != 2:
                raise ParserError(
                    "invalid metadata",
                    line_number,
                )
            content = parts[0].strip()
            metadata_text = "[" + parts[1]
        parts = content.split()

        if len(parts) != 3:
            raise ParserError(
                "invalid hub syntax",
                line_number,
            )
        name, x_text, y_text = parts
        if "-" in name:
            raise ParserError(
                "invalid hub name",
                line_number,
            )
        try:
            x = int(x_text)
            y = int(y_text)
        except ValueError:
            raise ParserError(
                "coordinate must be integer",
                line_number,
            )
        metadata = self.metadata_parser.parse(metadata_text, line_number)

        zone = metadata.get("zone", "normal")
        if zone not in self.VALID_ZONES:
            raise ParserError(
                f"invalid zone type {zone}",
                line_number,
            )
        color = metadata.get("color")
        max_drones: int | None = 1
        if "max_drones" in metadata:
            try:
                max_drones_str = metadata.get("max_drones")
                if max_drones_str is not None:
                    max_drones = int(max_drones_str)
                else:
                    max_drones = 1
            except ValueError:
                raise ParserError(
                    "max_drones must be an integer",
                    line_number,
                )
        if max_drones is not None and max_drones <= 0:
            raise ParserError(
                "max_drones must be positive",
                line_number,
            )

        if is_start or is_end:
            max_drones = None

        return Hub(
            name=name,
            x=x,
            y=y,
            zone=zone,
            color=color,
            max_drones=max_drones,
            is_start=is_start,
            is_end=is_end,
        )
