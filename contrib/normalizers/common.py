from collections import namedtuple

Field = namedtuple('Field', ['key', 'equ', 'unit', 'desc'])


class Normalizer:
    def __init__(self):
        self.normalizers = []

    def normalize(self, frame):
        for field in self.normalizers:
            try:
                key = field.key
                val = frame[key]
                frame[key] = field.equ(val)  # normalize
            except KeyError as e:
                print('Field {} not found in the frame '.format(key), e)

        return frame

    def get_unit(self, key):
        for field in self.normalizers:
            if key == field.key:
                return field.unit
