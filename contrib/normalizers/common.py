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
                frame['fields'][key] = {}
                frame['fields'][key]['value'] = field.equ(val)  # normalize
                frame['fields'][key]['unit'] = field.unit
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


def int2ddn(val):
    """
    Convert simple integer represented IP adresses into DDN (Dotted
    Decimal Notation)

    :param val: an IP address stored as integer

    :returns out: a string containing the DDN represented IP address
    """
    out = '{}.{}.{}.{}'.format((val & 0xFF000000) >> 24,
                               (val & 0x00FF0000) >> 16,
                               (val & 0x0000FF00) >> 8, (val & 0x000000FF))
    return out
