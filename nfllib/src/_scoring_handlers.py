#!
from __future__ import division, absolute_import

import itertools as it
from nfldb import PlayPlayer


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
        pass

    def calculate_score(self, pplayer):
        """

        :param pplayer: a single PlayPlayer
        :type pplayer: PlayPlayer
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
        self.passing_gt_400yds = cfg.get("passing_gt_400yds")
        self.passing_bonus = BonusHandler(cfg.get("passing_bonus"))

    def calculate_score(self, pplayer):
        score = 0.0

        # passing yards
        # TODO: abstract this behavior away
        per_yd = self.passing_yds["points"] / self.passing_yds["per"]
        score += pplayer.passing_yds * per_yd

        # passing tds
        score += pplayer.passing_tds * self.passing_td

        # ints
        score += pplayer.passing_int * self.int_thrown

        # 2 pt conversions
        score += pplayer.passing_twoptm

        # Apply bonuses
        # TODO: apply bonuses

        return score


class CatcherScoring(_ScoringHandler):

    def __init__(self, cfg):
        super(CatcherScoring, self).__init__(cfg)

        # Attributes
        self.receiving_yds = cfg.get("receiving_yds")
        self.receptions = cfg.get("receptions")
        self.receiving_tds = cfg.get("receiving_td")
        self.receiving_2pc = cfg.get("receiving_2pc")
        self.receiving_bonus = BonusHandler(cfg.get("receiving_bonus"))

    def calculate_score(self, pplayer):
        score = 0.0

        # TODO: abstract this away
        per_yd = self.receiving_yds["points"] / self.receiving_yds["per"]
        score += pplayer.receiving_yds * per_yd

        # TODO: abstract this away too
        per_reception = self.receptions["points"] / self.receiving_yds["per"]
        score += pplayer.receiving_rec * per_reception

        # tds
        score += pplayer.receiving_tds * self.receiving_tds

        # 2pt conversions
        score += pplayer.receiving_twoptm * self.receiving_2pc

        return score


class RunnerScoring(_ScoringHandler):

    def __init__(self, cfg):
        super(RunnerScoring, self).__init__(cfg)

        # Attributes
        self.rushing_yds = cfg.get("rushing_yds")
        self.rushing_td = cfg.get("rushing_td")
        self.rushing_2pc = cfg.get("rushing_2pc")
        self.rushing_bonus = BonusHandler(cfg.get("rushing_bonus"))

    def calculate_score(self, pplayer):
        score = 0.0

        # TODO: Abstract this away
        per_yd = self.rushing_yds["points"] / self.rushing_yds["per"]
        score += pplayer.rushing_yds * per_yd

        # TDs
        score += pplayer.rushing_tds * self.rushing_td

        # 2pt conversion
        score += pplayer.rushing_twoptm * self.rushing_2pc

        return score


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

    def calculate_score(self, pplayer):
        score = 0.0

        # PAT
        score += pplayer.kicking_xpmade * self.pat

        # PAT missed
        score += pplayer.kicking_xpmissed * self.pat_missed

        # score fg
        if pplayer.kicking_fgmissed:
            score += self.__score_fg(False, pplayer.kicking_fgmissed_yds)
        if pplayer.kicking_fgm:
            score += self.__score_fg(True, pplayer.kicking_fgm_yds)

        return score


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

    def calculate_score(self, pplayer):
        return 0


class Bonus(_ScoringHandler):

    def __init__(self, cfg):
        super(Bonus, self).__init__(cfg)

    def calculate_score(self, pplayer):
        return 0


class BonusHandler(_ScoringHandler):

    def __init__(self, cfg):
        super(BonusHandler, self).__init__(cfg)

    def calculate_score(self, pplayer):
        return 0