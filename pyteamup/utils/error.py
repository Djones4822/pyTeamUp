from urllib.error import HTTPError

class TeamUpError(HTTPError):
    """
    Error for Library to use when the response from the TeamUp API is invalid.
    """
    pass

