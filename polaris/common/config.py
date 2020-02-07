"""Module for PolarisConfig class
"""

import json
from collections import OrderedDict


# Disabling check for public methods; the python_json_config class has
# all the methods we need, and we're explicitly deferring to it.
class PolarisConfig(OrderedDict):  # pylint: disable=R0903
    """Class for Polaris configuration
    """

    DEFAULT_CONFIGFILE = "polaris_config.json"

    _DEFAULT_SETTINGS = {
        "root_dir": "/tmp/polaris",
        "cache_dir": "cache",
        "graph_dir": "graph",
        "log_dir": "log",
        "batch": {
            "learn": True,
            "fetch": True,
            "viz": False,
        }
    }

    def __init__(self, file=DEFAULT_CONFIGFILE, defaults=None):
        """Initialize Polaris configuration
        """
        defaults = defaults or self._DEFAULT_SETTINGS
        with open(file) as f_handle:
            OrderedDict.__init__(self, defaults)
            _data = json.load(f_handle)
            OrderedDict.update(self, _data)
