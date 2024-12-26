class KispyException(Exception):
    """Base class for all exceptions in Kispy."""

    pass


class KispyErrorResponse(KispyException):
    """Kispy error response."""

    err_code: str
    err_message: str

    def __init__(self, err_code: str, err_message: str):
        self.err_code = err_code
        self.err_message = err_message
        super().__init__(f"{err_code}: {err_message}")


class InvalidAccount(KispyException):
    """Invalid account."""

    pass


class InvalidSymbol(KispyException):
    """Invalid symbol."""

    pass
