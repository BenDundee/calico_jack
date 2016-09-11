#!
from __future__ import division, absolute_import

import itertools as it
from math import floor

from ._player_stats import PlayerStats


def _range_checker(x, lower, upper):
    """
    Return true if lower <= x <= upper, however, treats None as infinity.

    :param lower: bound
    :type lower: int
    :param upper: bound
    :type lower: int or None
    :return: lower <= x <= upper
    :rtype: bool
    """
    if x >= lower:
        if upper is None:
            return True
        else:
            return x <= upper
    return False


class _ScoringHandler(object):

    def __init__(self, cfg):
        self.__base_cfg = cfg.get("scoring", {})
        self.decimal_places = self.__base_cfg.get("decimal_places", 1)  # type: int

    def calculate_score(self, player_stats):
        """

        :param player_stats:
        :type player_stats: PlayerStats
        :return: A score
        :rtype: float
        """
        raise NotImplementedError("This method must be overridden")


class ThrowerScoring(_ScoringHandler):

    def __init__(self, cfg):
        super(ThrowerScoring, self).__init__(cfg)

        # Attributes
        self.passing_yds = cfg.get("passing_yds")
        self.int_thrown = cfg.get("int_thrown")
        self.passing_td = cfg.get("passing_td")
        self.passing_2pc = cfg.get("passing_2pc")
        self.passing_bonus = BonusHandler(cfg.get("passing_bonus"))

    def calculate_score(self, player_stats):
        """

        :param player_stats:
        :type player_stats: PlayerStats
        :return:
        :rtype: float
        """

        # Initialize score
        score = 0.0

        # passing yards
        # TODO: abstract this behavior away
        per_yd = self.passing_yds["points"] / self.passing_yds["per"]
        passing_score = player_stats.throwing["passing_yds"] * per_yd
        if not self.passing_yds["rules"]["allow_fractions"]:
            passing_score = floor(passing_score)
        score += passing_score

        # passing tds
        score += player_stats.throwing["passing_tds"] * self.passing_td

        # ints
        score += player_stats.throwing["int_thrown"] * self.int_thrown

        # 2 pt conversions
        score += player_stats.throwing["two_pt_made"] * self.passing_2pc

        # Apply bonuses
        # TODO: apply bonuses

        return round(score, self.decimal_places)


class CatcherScoring(_ScoringHandler):

    def __init__(self, cfg):
        super(CatcherScoring, self).__init__(cfg)

        # Attributes
        self.receiving_yds = cfg.get("receiving_yds")
        self.receptions = cfg.get("receptions")
        self.receiving_tds = cfg.get("receiving_td")
        self.receiving_2pc = cfg.get("receiving_2pc")
        self.receiving_bonus = BonusHandler(cfg.get("receiving_bonus"))

    def calculate_score(self, player_stats):
        """

        :param player_stats:
        :type player_stats: PlayerStats
        :return:
        :rtype: float
        """
        score = 0.0

        # TODO: abstract this away
        per_yd = self.receiving_yds["points"] / self.receiving_yds["per"]
        receiving_score = player_stats.catching["receiving_yds"] * per_yd
        if not self.receiving_yds["rules"]["allow_fractions"]:
            receiving_score = floor(receiving_score)
        score += receiving_score

        # TODO: abstract this away too
        per_reception = self.receptions["points"] / self.receptions["per"]
        reception_score = player_stats.catching["receptions"] * per_reception
        if not self.receptions["rules"]["allow_fractions"]:
            reception_score = floor(reception_score)
        score += reception_score

        # tds
        score += player_stats.catching["receiving_tds"] * self.receiving_tds

        # 2pt conversions
        score += player_stats.catching["receiving_twoptm"] * self.receiving_2pc

        return round(score, self.decimal_places)


class RunnerScoring(_ScoringHandler):

    def __init__(self, cfg):
        super(RunnerScoring, self).__init__(cfg)

        # Attributes
        self.rushing_yds = cfg.get("rushing_yds")
        self.rushing_td = cfg.get("rushing_td")
        self.rushing_2pc = cfg.get("rushing_2pc")
        self.rushing_bonus = BonusHandler(cfg.get("rushing_bonus"))

    def calculate_score(self, player_stats):
        """

        :param player_stats:
        :type player_stats: PlayerStats
        :return:
        :rtype: float
        """
        score = 0.0

        # TODO: Abstract this away
        per_yd = self.rushing_yds["points"] / self.rushing_yds["per"]
        rushing_score = player_stats.running["rushing_yds"] * per_yd
        if not self.rushing_yds["rules"]["allow_fractions"]:
            rushing_score = floor(rushing_score)
        score += rushing_score * per_yd

        # TDs
        score += player_stats.running["rushing_tds"] * self.rushing_td

        # 2pt conversion
        score += player_stats.running["two_pt_made"] * self.rushing_2pc

        return round(score, self.decimal_places)


class KickerScoring(_ScoringHandler):

    def __init__(self, cfg):
        super(KickerScoring, self).__init__(cfg)

        # Attributes
        self.pat = cfg.get("pat")
        self.pat_missed = cfg.get("pat_missed")

        # FG Scoring
        self.fg_scoring = cfg.get("fg_scores")

        # All field goals worth the same amount (may be 0).
        self._is_simple_scoring_model = type(self.fg_scoring) in (int, None)

        # Otherwise, use tiered model
        self._is_tiered_scoring_model = type(self.fg_scoring) is list

    def __score_fg(self, made, length):

        # Simple scoring model
        if self._is_simple_scoring_model:
            fgs_worth = 0 if self.fg_scoring is None else self.fg_scoring
            return fgs_worth if made else 0

        elif self._is_tiered_scoring_model:
            # Tiered makes and misses
            makes = sorted(
                (x for x in self.fg_scoring if x["action"] == "make")
                , key=lambda x: x["lower_bound"]
            )
            misses = sorted(
                (x for x in self.fg_scoring if x["action"] == "make")
                , key=lambda x: x["lower_bound"]
            )

            # Either make it or miss it. Another option?
            if made:
                # They're ordered, so take the first one
                tier = it.ifilter(lambda x: _range_checker(length, x["lower_bound"], x["upper_bound"]), makes).next()
            else:
                tier = it.ifilter(lambda x: _range_checker(length, x["lower_bound"], x["upper_bound"]), misses).next()
            return tier["points"]

        else:
            raise NotImplementedError("This field goal scoring method has not been invented yet!")

    def calculate_score(self, player_stats):
        """

        :param player_stats:
        :type player_stats: PlayerStats
        :return:
        :rtype: float
        """
        score = 0.0

        # PAT
        score += player_stats.kicking["xp_made"] * self.pat

        # PAT missed
        score += player_stats.kicking["xp_missed"] * self.pat_missed

        # score fg
        if player_stats.kicking["made"]:
            for yds in player_stats.kicking["made_lengths"]:
                score += self.__score_fg(True, yds)
        if player_stats.kicking["missed"]:
            for yds in player_stats.kicking["missed_lengths"]:
                score += self.__score_fg(False, yds)

        return round(score, self.decimal_places)


class DefStScoring(_ScoringHandler):

    def __init__(self, cfg):
        super(DefStScoring, self).__init__(cfg)

        # Attributes
        self.kickoff_return_td = cfg.get("kickoff_return_td")
        self.punt_return_td = cfg.get("punt_return_td")
        self.fumble_rec_td = cfg.get("fumble_rec_td")
        self.fumble_ret_td = cfg.get("fumble_ret_td")
        self.fumble_lost = cfg.get("fumble_lost")
        self.int_ret_td = cfg.get("int_ret_td")
        self.blk_punt_td = cfg.get("blk_punt_td")
        self.blk_fg_td = cfg.get("blk_fg_td")
        self.two_pt_return = cfg.get("two_pt_return")
        self.one_pt_safety = cfg.get("one_pt_safety")
        self.sack = cfg.get("sack")
        self.block = cfg.get("block")
        self.def_int = cfg.get("def_int")
        self.def_safety = cfg.get("def_safety")
        self.fumble_rec = cfg.get("fumble_rec")

        # pts
        self.def_points_allowed = cfg.get("def_points_allowed")

        # yds
        self.def_yds_allowed = cfg.get("def_yds_allowed")

    def calculate_score(self, player_stats):
        """

        :param player_stats:
        :type player_stats: PlayerStats
        :return:
        :rtype: float
        """
        score = 0.0

        # Regular defensive stuff
        score += player_stats.d_st["fumble_lost"] * self.fumble_lost
        score += player_stats.d_st["fumble_rec"] * self.fumble_rec
        score += player_stats.d_st["int"] * self.def_int

        # Punt stuff

        # score += pplayer.

        return round(score, self.decimal_places)


class _BonusHandler(object):

    def __init__(self, cfg):
        self.__base_cfg = cfg

    def calculate_score(self, player_stats):
        pass


class Bonus(_BonusHandler):

    def __init__(self, cfg):
        super(Bonus, self).__init__(cfg)

    def calculate_score(self, player_stats):
        pass


class BonusHandler(_BonusHandler):

    def __init__(self, cfg):
        super(BonusHandler, self).__init__(cfg)

    def calculate_score(self, player_stats):
        pass