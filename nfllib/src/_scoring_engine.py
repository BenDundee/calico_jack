#!
from __future__ import absolute_import

from ._scoring_method import ScoringMethod


class ScoringEngine(object):

    def __init__(self, cfg_location):

        self.scoring_method = ScoringMethod(cfg_location)

        # For leagues that use DST instead of IDP
        self.aggregate_dst_scoring = True

    def score(self, line):
        self.scoring_method.calculate_score(line)