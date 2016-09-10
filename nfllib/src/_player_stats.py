#!

from __future__ import division, absolute_import

import itertools as it
from nfldb import Game


def _calculate_qbr(dat):
    """
    see, eg, https://en.wikipedia.org/wiki/Passer_rating#NFL_and_CFL_formula

    :param dat:
    :return: float
    """

    # Completion pct
    a = ((dat["complete"] / dat["attempts"]) - 0.3) * 5.0

    # Yds/att
    b = ((dat["passing_yds"] / dat["attempts"]) - 3.0) * 0.25

    # TD ratio
    c = (dat["passing_tds"] / dat["attempts"]) * 20.0

    # INT penalty
    d = 2.375 - (dat["int_thrown"] / dat["attempts"]) * 25.0

    # Enforce 0 <= result <= 2.375
    def __f(r):
        if r < 0:
            return 0
        elif r > 2.375:
            return 2.375
        else:
            return r

    a = __f(a)
    b = __f(b)
    c = __f(c)
    d = __f(d)
    return (
        (a + b + c + d) * 100.0 / 6.0
    )


class PlayerStats(object):

    def __init__(self, player_id):
        """

        :param player_id: player id, looks like `00-0027949`
        :type player_id: basestring
        """

        self.player_id = player_id
        self.game_list = []

        self.throwing = {
            "attempts": 0
            , "complete": 0
            , "passing_yds": 0
            , "int_thrown": 0
            , "passing_tds": 0
            , "passing_td_lengths": []
            , "completion_lengths": []
            , "two_pt_made": 0
        }

        self.running = {
            "attempts": 0
            , "rushing_yds": 0
            , "rushing_tds": 0
            , "rush_lengths": []
            , "rush_td_lengths": []
            , "two_pt_made": 0
        }

        self.catching = {
            "targets": 0
            , "receiving_rec": 0
            , "receiving_yds": 0
            , "receiving_tds": 0
            , "receiving_twoptm": 0
            , "reception_lengths": []
            , "td_lengths": []
        }

        self.kicking = {
            "attempts": 0
            , "attempt_legths": []
            , "made": 0
            , "made_lengths": []
            , "xp_attempts": 0
            , "xp_made": 0
        }

        # D/ST scoring. Include all fumbles/ints here
        self.d_st = {
            "int": 0
            , "int_ret_yds": []
            , "fumble_lost": 0
            , "fumble_rec": 0
        }

    @property
    def qbr(self):
        return round(_calculate_qbr(self.throwing), 1)

    def add_game(self, game):
        """

        :param game:
        :type game: Game
        """

        # Only need the relevant player...
        for p in it.ifilter(lambda x: x.player_id == self.player_id, game.play_players):

            #
            # Passing
            #
            self.throwing["passing_yds"] += p.passing_yds
            self.throwing["passing_tds"] += p.passing_tds
            self.throwing["attempts"] += p.passing_att
            self.throwing["complete"] += p.passing_cmp
            self.throwing["int_thrown"] += p.passing_int
            self.throwing["two_pt_made"] += p.passing_twoptm

            if p.passing_cmp:
                self.throwing["completion_lengths"].append(p.passing_yds)
            if p.passing_tds:
                self.throwing["passing_td_lengths"].append(p.passing_yds)

            #
            # Running
            #
            self.running["attempts"] += p.rushing_att
            self.running["rushing_yds"] += p.rushing_yds
            self.running["rushing_tds"] += p.rushing_tds
            self.running["two_pt_made"] += p.rushing_twoptm

            if p.rushing_att:
                self.running["rush_lengths"].append(p.rushing_yds)
            if p.rushing_tds:
                self.running["rush_td_lengths"].append(p.rushing_yds)

            #
            # Receiving
            #
            self.catching["targets"] += p.receiving_tar
            self.catching["receiving_rec"] += p.receiving_rec
            self.catching["receiving_yds"] += p.receiving_yds
            self.catching["receiving_tds"] += p.receiving_tds
            self.catching["receiving_twoptm"] += p.receiving_twoptm

            if p.receiving_rec:
                self.catching["reception_lengths"].append(p.receiving_yds)
            if p.receiving_tds:
                self.catching["receiving_tds"].append(p.receiving_tds)

            #
            # Kicking
            #
            self.kicking["attempts"] += p.kicking_fga
            self.kicking["made"] += p.kicking_fgm
            self.kicking["xp_attempts"] += p.kicking_xpa
            self.kicking["xp_made"] += p.kicking_xpmade

            if p.kicking_fga:
                if p.kicking_fgm:
                    self.kicking["made_lengths"].append(p.kicking_fgm_yds)
                else:
                    self.kicking["attempt_legths"].append(p.kicking_fga_yds)

            #
            # Defense/ST
            #
            self.d_st["int"] += p.defense_int
            self.d_st["int_ret_yds"] += p.defense_int_yds
            self.d_st["fumble_lost"] += p.fumbles_lost
            self.d_st["fumble_rec"] += p.fumbles_rec

        # extend list
        self.game_list.append(game.gsis_id)

    def add_games(self, games):
        """

        :param games:
        :type games: list[Game]
        """
        _ = [self.add_game(g) for g in games]


if __name__ == "__main__":

    from nfldb import connect, Query

    # RGIII throws perfect game as a rookie against Philly
    _gsis_id = "2012111800"
    _player_id = "00-0029665"

    conn = connect()
    q = Query(conn)
    _ = q.game(gsis_id=_gsis_id)
    stats = PlayerStats(_player_id)
    stats.add_games(q.as_games())
    assert len(stats.game_list) == 1

    # Line: 14/15, 200yds, 4TD, 0 INT, 12 rushes for 84 yds.

    qbr = stats.qbr
    assert round(stats.qbr, 1) == 158.3
