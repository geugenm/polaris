"""This module holds the JsonSerializable class
"""

import json


class JsonSerializable():
    """Class for JSON-serializable objects
    """

    def to_json(self):
        """Write a dataset object to JSON.
        """
        return json.dumps(self, indent=4)

    def from_json(self, json_string):
        """Load a dataset object from a JSON string

        :param json_string: a string of JSON to read from.
        """
        _obj = json.loads(json_string)
        self.__init__(_obj)
