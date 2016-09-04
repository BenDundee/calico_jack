#!
from __future__ import absolute_import
from nfldb import connect
from os import path

from nfllib.src._configurable import Configurable
from nfllib.src._scoring_method import ScoringMethod
from nfllib.src._team import FantasyTeam


DEFAULT_FILE_LOCATION = "config/game.pcfg"
_FACTORY = {
    "scoring_method": ScoringMethod
    , "fantasy_team": FantasyTeam
}


class GameEngine(Configurable):

    def __init__(self, game_cfg=None):
        self.stub = path.abspath(path.dirname(__file__)) + "/../{0}"
        if game_cfg is None:
            game_cfg = self.stub.format(DEFAULT_FILE_LOCATION)
        super(GameEngine, self).__init__(game_cfg)

        # DB Connection
        self._conn = connect()

        # Game elements
        self.scoring_method = self._config_handler("scoring_method")
        self.fantasy_team = self._config_handler("fantasy_team", conn=self._conn)

    def _config_handler(self, tag, **kwargs):
        if path.isfile(self.config[tag]):
            fn = self.config[tag]
        else:
            fn = "{0}/{1}".format(path.dirname(self.cfg_location), self.config[tag])
        return _FACTORY[tag](cfg_location=fn, **kwargs)

    def score(self, line):
        self.scoring_method.calculate_score(line)


if __name__ == "__main__":

    engine = GameEngine()


