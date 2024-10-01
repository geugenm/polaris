from polaris.common.json_serializable import JsonSerializable


class PolarisFrame(dict, JsonSerializable):
    def __init__(self, frame=None):
        dict.__init__(self)
        JsonSerializable.__init__(self)
        if frame is not None:
            for key, value in frame.items():
                self[key] = value
