"""Error class definitions for num2vid and associated modules."""
import logging


class Num2VidServerError(Exception):
    """Base Exception class.

    :attr msg: message str given from raiser.
    :type msg: str
    """
    def __init__(self, msg: str, *args: ..., **kwargs: ...):
        """Initialize with message str.

        :param msg: message describing exception from raiser.
        """
        super(Num2VidServerError, self).__init__(*args, **kwargs)
        self.msg = msg
        logging.error(self.__repr__())

    def __str__(self):
        return "<{error}: {msg}>".format(error=self.__class__.__name__, msg=self.msg)


class InvalidMathStrError(Num2VidServerError):
    """The math string provided was not valid."""


class InvalidMathStrResultError(Num2VidServerError):
    """The result of the math str is invalid and unsafe."""


class Num2VidClientError(Exception):
    """Base Exception class for Num2VidClient.

    :attr msg: message str given from raiser.
    :type msg: str
    """
    def __init__(self, msg: str, *args: ..., **kwargs: ...):
        """Initialize with message str.

        :param msg: message describing exception from raiser.
        """
        super(Num2VidClientError, self).__init__(*args, **kwargs)
        self.msg = msg
        logging.error(self.__repr__())

    def __str__(self):
        return "<{error}: {msg}>".format(error=self.__class__.__name__, msg=self.msg)


class ConnectionError(Num2VidClientError):
    """Unable to connect to Num2Vid Server."""


class Num2VidConfigError(Exception):
    """Base class for all Num2Vid client exceptions.

    :attr err: Exception object given from raiser.
    :type err: Exception
    """
    def __init__(self, err: Exception, *args: ..., **kwargs: ...):
        """Initialize with message str.

        :param err: Original Exception thrown.
        """
        super(Num2VidConfigError, self).__init__(*args, **kwargs)
        self.err = err


class ConfigPathError(Num2VidConfigError):
    """Unable to read from the given filepath."""


class ConfigReadError(Num2VidConfigError):
    """Unable to parse contents of config to dict."""
