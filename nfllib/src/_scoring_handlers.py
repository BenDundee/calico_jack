#!
from __future__ import division

from nfldb import PlayPlayer


class _ScoringHandler(object):

    def __index__(self, cfg):
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
        self.passing_yds = cfg.get("passing_yds")
        self.int_thrown = cfg.get("int_thrown")
        self.passing_td = cfg.get("passing_td")
        self.passing_2pc = cfg.get("passing_2pc")
        self.passing_gt_400yds = cfg.get("passing_gt_400yds")
        self.passing_bonus = BonusHandler(cfg.get("passing_bonus"))

    def calculate_score(self, pplayer):
        """

        :param pplayer: a single PlayPlayer
        :type pplayer: PlayPlayer
        :return: A score
        :rtype: float
        """
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
        self.receiving_yds = cfg.get("receiving_yds")
        self.receptions = cfg.get("receptions")
        self.receiving_tds = cfg.get("receiving_td")
        self.receiving_2pc = cfg.get("receiving_2pc")
        self.receiving_bonus = BonusHandler(cfg.get("receiving_bonus"))

    def calculate_score(self, pplayer):
        """

        :param pplayer: a single PlayPlayer
        :type pplayer: PlayPlayer
        :return: A score
        :rtype: float
        """
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
        self.rushing_yds = cfg.get("rushing_yds")
        self.rushing_td = cfg.get("rushing_td")
        self.rushing_2pc = cfg.get("rushing_2pc")
        self.rushing_bonus = BonusHandler(cfg.get("rushing_bonus"))

    def calculate_score(self, pplayer):
        """

        :param pplayer: a single PlayPlayer
        :type pplayer: PlayPlayer
        :return: A score
        :rtype: float
        """
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
        self.pat = cfg.get("pat")
        self.fg_scores = cfg.get("fg_scores")

    def calculate_score(self, pplayer):
        """

        :param pplayer: a single PlayPlayer
        :type pplayer: PlayPlayer
        :return: A score
        :rtype: float
        """
        return 0


class DefStScoring(_ScoringHandler):

    def __init__(self, cfg):
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
        """

        :param pplayer: a single PlayPlayer
        :type pplayer: PlayPlayer
        :return: A score
        :rtype: float
        """
        return 0


class Bonus(_ScoringHandler):

    def __init__(self, cfg):
        pass

    def calculate_score(self, pplayer):
        return 0


class BonusHandler(_ScoringHandler):

    def __init__(self, cfg):
        pass

    def calculate_score(self, pplayer):
        return 0