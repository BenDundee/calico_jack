#!

import itertools as it
from os import path
from nfldb import Play
from yaml import load

from _scoring_handlers import ThrowerScoring, CatcherScoring, RunnerScoring, KickerScoring, DefStScoring
from _scoring_handlers import Bonus, BonusHandler


DEFAULT_FILE_LOCATION = "config/scoring.cfg"


class ScoringMethod(object):
    """
    A class designed to return the fantasy score of a set of plays.

    """

    def __init__(self, cfg_location=None):
        """

        :param cfg_location: Location of scoring config file
        """
        self.stub = path.abspath(path.dirname(__file__)) + "/{0}"
        self.config = self._get_scoring_method(cfg_location)

        # Scoring handlers
        self.thrower_scoring = ThrowerScoring(self.config.get("thrower_scoring"))
        self.catcher_scoring = CatcherScoring(self.config.get("catcher_scoring"))
        self.runner_scoring = RunnerScoring(self.config.get("runner_scoring"))
        self.kicker_scoring = KickerScoring(self.config.get("kicker_scoring"))
        self.def_st_scoring = DefStScoring(self.config.get("def_st_scoring"))

        # Add a convenience method to make scoring easier
        self._scoring_handlers = [
            self.thrower_scoring.calculate_score
            , self.catcher_scoring.calculate_score
            , self.runner_scoring.calculate_score
            , self.kicker_scoring.calculate_score
            , self.def_st_scoring.calculate_score
        ]
        self.apply_handlers = lambda x: sum(score(x) for score in self._scoring_handlers)

    def calculate_score(self, plays):
        """

        :param plays: a list of plays
        :type plays: list[Play]
        :return: dict[Player, int]
        :rtype: dict[Player, int]
        """
        score = {}
        player_ids = []
        for p in it.chain.from_iterable(p.play_players for p in plays):

            # Are we already tracking this player?
            if p.player.player_id not in player_ids:
                score[p.player.player_id] = 0
                player_ids.append(p.player.player_id)

            # update scoring
            score[p.player.player_id] += self.apply_handlers(p)

        return score

    def _get_scoring_method(self, cfg_location=None):
        if not cfg_location:
            cfg_location = self.stub.format(DEFAULT_FILE_LOCATION)
        return load(file(cfg_location, 'r'))


if __name__ == "__main__":
    import nfldb as nfl

    db = nfl.connect()
    sm = ScoringMethod()

    q = nfl.Query(db)
    _ = q.play(gsis_id="2009081350")
    score = sm.calculate_score(q.as_plays())

    print 'break!'
