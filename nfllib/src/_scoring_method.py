#!
from __future__ import absolute_import, division

from nfllib.src._scoring_handlers import ThrowerScoring, CatcherScoring, RunnerScoring, KickerScoring, DefStScoring
from nfllib.src._configurable import Configurable
from nfllib.src._player_stats import PlayerStats


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
        self.__apply_handlers = lambda x: sum(score(x) for score in self._scoring_handlers)

    def calculate_score(self, player_stats):
        """

        :param player_stats:
        :type player_stats: PlayerStats
        :return: mapping of player id to score
        :rtype: float
        """
        return self.__apply_handlers(player_stats)


if __name__ == "__main__":
    from itertools import ifilter
    import nfldb as nfl
    from os import path

    cfg_loc = path.abspath(path.dirname(__file__)) + "/../config/scoring.pcfg"
    sm = ScoringMethod(cfg_loc)

    db = nfl.connect()
    q = nfl.Query(db)
    _ = q.game(gsis_id="2009081350")

    gm = q.as_games()[0]
    stats = [PlayerStats(p[1].player_id) for p in gm.players]
    _ = [p.add_game(gm) for p in stats]
    scores = {
        p.player_id: sm.calculate_score(p) for p in stats
    }

    print('break!')

    # Look at a single player
    # Onrea Jones
    # 2 rec., 43 yds, 1 TD (20)
    stat = ifilter(lambda x: x.player_id == '00-0024645', stats).next()
    score = sm.calculate_score(stat)
    assert score == 11.0

    print('break')
