import logging
from collections import namedtuple

LOGGER = logging.getLogger(__name__)

Field = namedtuple('Field', ['key', 'equ', 'unit', 'desc'])


class Normalizer:
    def __init__(self):
        self.normalizers = []

    def normalize(self, frame):
        missing_keys = False

        for field in self.normalizers:
            try:
                key = field.key
                val = frame['fields'][key]
                frame['fields'][key] = field.equ(val)  # normalize
            except KeyError:
                missing_keys = True
                LOGGER.debug('Field %s not found in the frame', key)

        if missing_keys:
            LOGGER.warning('Some fields could not be normalized')

        return frame

    def get_unit(self, key):
        for field in self.normalizers:
            if key == field.key:
                return field.unit
