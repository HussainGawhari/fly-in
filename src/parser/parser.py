from pathlib import Path

from src.exception import ParserError
from src.models.connection import Connection
from src.models.hub import Hub
from src.models.map import FlyMap
from src.parser.connection_parser import ConnectionParser
from src.parser.hub_parser import HubParser


class MapParser:
    """Loads a map file and builds the in-memory graph model."""

    def __init__(self) -> None:
        """Create the specialized parsers used for hubs and connections."""
        self.hub_parser = HubParser()
        self.connection_parser = ConnectionParser()

    def parse_file(self, path: Path) -> FlyMap:
        """Parse the map file and return the fully built FlyMap object."""
        lines = path.read_text(encoding="utf-8").splitlines()

        nb_drones: int | None = None
        hubs: dict[str, Hub] = {}
        connections: list[Connection] = []

        start_hub: str | None = None
        end_hub: str | None = None

        for line_number, row_line in enumerate(lines, start=1):
            line = row_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("nb_drones:"):
                if nb_drones is not None:
                    raise ParserError(
                        "Dublicate nb_drones",
                        line_number,
                    )
                value = line[len("nb_drones:"):].strip()

                try:
                    nb_drones = int(value)
                except ValueError:
                    raise ParserError(
                        "nb_drones must be an integer",
                        line_number,
                    )
                if nb_drones <= 0:
                    raise ParserError(
                        "nb_drones must be positive intger",
                        line_number,
                    )
            elif line.startswith("start_hub:"):
                if start_hub is not None:
                    raise ParserError(
                        "duclicate start_hub",
                        line_number,
                    )
                content = line[len("start_hub:"):].strip()
                hub = self.hub_parser.parse(
                    content,
                    line_number,
                    is_start=True,
                )
                self._add_hub(
                    hubs,
                    hub,
                    line_number,
                )
                start_hub = hub.name
            elif line.startswith("end_hub:"):
                if end_hub is not None:
                    raise ParserError(
                        "Dulicate end_hub",
                        line_number,
                    )
                content = line[len("end_hub:"):].strip()
                hub = self.hub_parser.parse(
                    content,
                    line_number,
                    is_end=True,
                )
                self._add_hub(
                    hubs,
                    hub,
                    line_number
                )
                end_hub = hub.name
            elif line.startswith("hub:"):
                content = line[len("hub:"):].strip()
                hub = self.hub_parser.parse(
                    content,
                    line_number,
                )
                self._add_hub(
                    hubs,
                    hub,
                    line_number,
                )

            elif line.startswith("connection:"):
                content = line[len("connection:"):].strip()
                connection = self.connection_parser.parse(
                    content,
                    line_number,
                )
                self._valided_connection(
                    connection,
                    hubs,
                    connections,
                    line_number,
                )

                connections.append(connection)

            else:
                raise ParserError(
                    "unknow syntax",
                    line_number,
                )
        if nb_drones is None:
            raise ParserError(
                "missing nb_drones",
                line_number,
                )
        if start_hub is None:
            raise ParserError(
                "missing start_hub",
                line_number,
                )
        if end_hub is None:
            raise ParserError(
                "missing end_hub",
                line_number,
                )

        return FlyMap(
            nb_drones=nb_drones,
            hubs=hubs,
            connections=connections,
            start_hub=start_hub,
            end_hub=end_hub
        )

    @staticmethod
    def _add_hub(
        hubs: dict[str, Hub],
        hub: Hub,
        line_number: int
    ) -> None:
        if hub.name in hubs:
            raise ParserError(
                f"duplicate hubs {hub.name}",
                line_number,
            )
        hubs[hub.name] = hub

    @staticmethod
    def _valided_connection(
        connection: Connection,
        hubs: dict[str, Hub],
        connections: list[Connection],
        line_number: int,
    ) -> None:

        if connection.hub1 not in hubs:
            raise ParserError(
                f"unknown hub {connection.hub1}",
                line_number,
            )
        if connection.hub2 not in hubs:
            raise ParserError(
                f"unknown hub {connection.hub2}",
                line_number,
            )
        for existing in connections:
            if existing.key == connection.key:
                raise ParserError(
                    f"Duplicate connection "
                    f"{connection.hub1} - {connection.hub2}",
                    line_number,
                )
