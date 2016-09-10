#!
from __future__ import absolute_import, division

import itertools as it
from nfldb import PlayPlayer
from os import path

from nfllib.src._scoring_handlers import ThrowerScoring, CatcherScoring, RunnerScoring, KickerScoring, DefStScoring
from nfllib.src._configurable import Configurable


class ScoringMethod(Configurable):
    """ A class designed to return the fantasy score of a set of plays.

    """
    def __init__(self, cfg_location):
        """

        :param cfg_location: Location of scoring config file
        :type cfg_location: basestring
        """
        super(ScoringMethod, self).__init__(cfg_location)

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

    def calculate_score(self, play_players):
        """

        :param play_players: a list of plays
        :type play_players: list[PlayPlayer]
        :return: mapping of player name to score
        :rtype: dict[str, float]
        """
        score = {}
        player_ids = []
        for p in play_players:

            # Are we already tracking this player?
            if p.player.player_id not in score:
                score[p.player.player_id] = 0

            # update scoring
            score[p.player.player_id] += self.apply_handlers(p)

        return score


if __name__ == "__main__":
    import nfldb as nfl

    cfg_loc = path.abspath(path.dirname(__file__)) + "/../config/scoring.pcfg"
    sm = ScoringMethod(cfg_loc)

    db = nfl.connect()
    q = nfl.Query(db)
    _ = q.play(gsis_id="2009081350")
    _score = sm.calculate_score(q.as_plays())

    print('break!')
