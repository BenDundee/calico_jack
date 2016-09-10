#!
from __future__ import absolute_import
from nfldb import connect, Query
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

        # TODO: refactor FantasyTeam class so that it doesn't need the db connection
        self.fantasy_team = self._config_handler("fantasy_team", conn=self._conn)

    def _config_handler(self, tag, **kwargs):
        if path.isfile(self.config[tag]):
            fn = self.config[tag]
        else:
            fn = "{0}/{1}".format(path.dirname(self.cfg_location), self.config[tag])
        return _FACTORY[tag](cfg_location=fn, **kwargs)

    def score(self, line):
        return self.scoring_method.calculate_score(line)

    def score_game(self, gsis_id, player_id=None):
        """ Score a game

        Scores a game, given it's id. If `player` is `None`, the scores of all players are returned. If `player` is not
        `None`, the game is filtered so that only those plays in which the specific player was involved are scored. It
        is expected to be generally faster.

        :param gsis_id: gsis_id of game
        :type gsis_id: basestring
        :param player_id: player id
        :type player_id: basestring
        :return: game score by player
        :rtype: dict[str, double]
        """
        q = Query(self._conn)
        _ = q.game(gsis_id=gsis_id)
        if player_id is not None:
            _ = q.player(player_id=player_id)

        # get score
        return self.scoring_method.calculate_score(q.as_play_players())

    def _score_defense(self, game):
        """
        Calculate score by the defense. The most common case is also the most complicated--combining defense and special
        teams into a single unit.

        :param game:
        :return:
        """
        return 0.0


if __name__ == "__main__":

    engine = GameEngine()
    #score1 = engine.score_game(gsis_id="2009081350")
    #print('break!')

    score2 = engine.score_game(gsis_id="2009081350", player_id="00-0022924")
    print('break!')

