from src.exception import ParserError

"""we will parse: [zone=restricted color=red max_drones=2]  """


class MetadataParser:

    def parse(
            self,
            text: str,
            line_number: int,
    ) -> dict[str, str]:

        text = text.strip()

        if not text:
            return {}
        if not text.startswith("[") or not text.endswith("]"):
            raise ParserError(
                "invalid metada structure",
                line_number,
            )
        content = text[1: -1].strip()

        if not content:
            return {}

        metadata: dict[str, str] = {}
        for item in content.split():
            if "=" not in item:
                raise ParserError(
                    f"invalid metadata {item} ",
                    line_number,
                )

            key, value = item.split("=", 1)
            if not key or not value:
                raise ParserError(
                    f"invalid metadata '{item}'",
                    line_number,
                )

            if key in metadata:
                raise ParserError(
                    f"duplicate metadata '{key}'",
                    line_number,
                )

            metadata[key] = value

        return metadata
