"""

pyTeamUp

Python Library for interfacing with the TeamUp api

"""

__version__ = '0.0.1a'
__author__ = 'David Jones'

from Calendar import Calendar
from Event import Event

# Set default logging handler to avoid "No handler found" warnings.  ## STOLEN FROM https://github.com/nithinmurali/pygsheets/blob/staging/pygsheets/__init__.py thanks Nithin :)
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())