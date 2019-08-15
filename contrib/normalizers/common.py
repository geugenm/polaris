import logging
from collections import namedtuple

LOGGER = logging.getLogger(__name__)

Field = namedtuple('Field', ['key', 'equ', 'unit', 'desc'])


class Normalizer:
    def __init__(self):
        self.normalizers = []

    def normalize(self, frame):
        for field in self.normalizers:
            try:
                key = field.key
                val = frame['fields'][key]
                frame['fields'][key] = field.equ(val)  # normalize
            except KeyError as e:
                LOGGER.warning('Field %s not found in the frame', key)

        return frame

    def get_unit(self, key):
        for field in self.normalizers:
            if key == field.key:
                return field.unit
