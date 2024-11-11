class KispyException(Exception):
    """Base class for all exceptions in Kispy."""

    pass


class InvalidAccount(KispyException):
    """Invalid account."""

    pass


class InvalidSymbol(KispyException):
    """Invalid symbol."""

    pass
