#!
from yaml import load


class Configurable(object):

    def __init__(self, cfg_location):
        self.cfg_location = cfg_location
        self.config = self._get_config_file()

    def _get_config_file(self):
        with open(self.cfg_location, 'r') as f:
            return load(f)
