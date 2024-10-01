import json

import pandas as pd

from polaris.common import constants
from polaris.common.json_serializable import JsonSerializable
from polaris.dataset.frame import PolarisFrame
from polaris.dataset.metadata import PolarisMetadata


class PolarisDataset(dict, JsonSerializable):
    def __init__(self, metadata=None, frames=None):
        dict.__init__(self)
        JsonSerializable.__init__(self)
        self.metadata = PolarisMetadata(metadata)
        if isinstance(frames, list):
            self.frames = [PolarisFrame(frame) for frame in frames]
        else:
            self.frames = [PolarisFrame(frames)]

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return self.to_json()

    def from_json(self, json_string):
        _obj = json.loads(json_string)
        self.__init__(metadata=_obj['metadata'], frames=_obj['frames'])

    def to_json(self):
        return json.dumps({
            "metadata": self.metadata,
            "frames": self.frames
        },
            indent=constants.JSON_INDENT)

    def to_pandas_dataframe(self):
        records = []
        for frame in self.frames:
            fields = {}
            for field in frame['fields']:
                try:
                    fields[field] = frame['fields'][field]['value']
                except Exception as e:
                    print("Exception: {}, field: {}".format(e, field))
                    print("frame['fields'][field]: {}".format(
                        frame['fields'][field]))
                    continue

            if "time" not in fields:
                fields['time'] = pd.to_datetime(frame['time']).timestamp()

            records.append(fields)

        return pd.DataFrame(records)
