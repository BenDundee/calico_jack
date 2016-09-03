#!

import itertools as it
from os import path
from nfldb import Player, Team

from nfllib.src._configurable import Configurable


DEFAULT_FILE_LOCATION = "config/team.pcfg"


class FantasyTeam(Configurable):

    def __init__(self, cfg_location=None):
        """

        :param cfg_location: location of config file
        :type cfg_location: str
        """
        self.stub = path.abspath(path.dirname(__file__)) + "/../{0}"
        if cfg_location is None:
            cfg_location = self.stub.format(DEFAULT_FILE_LOCATION)
        super(FantasyTeam, self).__init__(cfg_location)

        # team
        self.qb = self.config.get("qb")
        self.rb = self.config.get("rb")
        self.wr = self.config.get("wr")
        self.te = self.config.get("te")
        self.def_ = self.config.get("def")
        self.k = self.config.get("k")
        self.flex = self.config.get("flex")

    @property
    def starters(self):
        return {
            "qb": self.qb.get("starters")
            , "rb": self.rb.get("starters")
            , "wr": self.wr.get("starters")
            , "te": self.te.get("starters")
            , "def": self.def_.get("starters")
            , "k": self.k.get("starters")
            , "flex": self.flex.get("starters")
        }

    @property
    def bench(self):
        return {
            "qb": self.qb.get("bench")
            , "rb": self.rb.get("bench")
            , "wr": self.wr.get("bench")
            , "te": self.te.get("bench")
            , "def": self.def_.get("bench")
            , "k": self.k.get("bench")
            , "flex": self.flex.get("bench")
        }

if __name__ == "__main__":

    team = FantasyTeam()
    starters = team.starters
    bench = team.bench

    print("break!")