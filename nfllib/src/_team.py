#!
from __future__ import absolute_import

from os import path
from nfldb import Query, player_search, connect, standard_team

from nfllib.src._configurable import Configurable


def _player_lookup(player, conn):
    try:
        q = Query(conn)
        p = q.player(full_name=player).as_players()
        if len(p) == 1:
            return p[0].full_name, p[0].player_id
        else:
            similar = "\n\t* ".join(x[0].full_name for x in player_search(conn, s, limit=3))
            msg = "{0} could not be found in player DB. Similar results:\n\t* {1}".format(s, similar)
            raise Exception(msg)
    except Exception as e:
        raise Exception("Error looking up names, details follow. {0}".format(e))


def _defense_lookup(d, conn):
    t = standard_team(d)
    if t != 'UNK':
        return (t, t), False
    else:
        return _player_lookup(d, conn), True


def _get_player(dat, conn):
    return {
        "starters": [_player_lookup(s, conn) for s in dat.get("starters", [])]
        , "bench": [_player_lookup(b, conn) for b in dat.get("bench", [])]
    }


def _get_defense(dat, conn):
    starters = [_defense_lookup(s, conn) for s in dat.get("starters", [])]
    bench = [_defense_lookup(b, conn) for b in dat.get("bench", [])]
    is_idp = all(x[-1] for x in starters) and (all(x[-1] for x in bench))
    return {
        "starters": [x[0] for x in starters]
        , "bench": [x[0] for x in bench]
    }, is_idp


class FantasyTeam(Configurable):

    def __init__(self, conn, cfg_location):
        """

        :param conn: connection object (returned by nfldb.connect())
        :type conn: psycopg2._psycopg.connection
        :param cfg_location: location of config file
        :type cfg_location: str
        """
        super(FantasyTeam, self).__init__(cfg_location)

        # team
        self.qb = _get_player(self.config.get("qb", {}), conn)
        self.rb = _get_player(self.config.get("rb", {}), conn)
        self.wr = _get_player(self.config.get("wr", {}), conn)
        self.te = _get_player(self.config.get("te", {}), conn)
        self.k = _get_player(self.config.get("k", {}), conn)
        self.flex = _get_player(self.config.get("flex", {}), conn)

        # Defense separately
        self.def_, self.is_idp = _get_defense(self.config.get("def", {}), conn)

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

    cfg_loc = path.abspath(path.dirname(__file__)) + "/../config/team.pcfg"
    db = connect()
    team = FantasyTeam(db, cfg_loc)
    _starters = team.starters
    _bench = team.bench

    print("break!")