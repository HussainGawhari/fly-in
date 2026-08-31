class ParserError(Exception):
    """Raised when a map file cannot be parsed.

    The exception keeps the failing line number when available so the user
    can locate the exact problem in the input file.
    """

    def __init__(self, message: str, line_number: int | None) -> None:
        """Store the error message and optional file line for debugging.

        The line number is added to the text so parsing failures are easier to
        trace during map validation.
        """
        self.line_number = line_number

        if line_number is not None:
            message = f"line {line_number}: {message}"
        super().__init__(message)
