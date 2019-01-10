import pytest

from maketeams3 import get_player_data, process_friends_and_avoid, \
    old_process_friends_and_avoid, make_league


def test_new_process_players_fun():
    players = './ignore/s15anon.json'
    boards=6
    balance=0.8

    player_data = get_player_data(players)

    leagues = [make_league(player_data, boards, balance, fun) for
               fun in
               [process_friends_and_avoid, old_process_friends_and_avoid]]
    for ta, tb in zip(leagues[0]['teams'], leagues[1]['teams']):
        assert([p.name for p in ta.boards] == [p.name for p in tb.boards])
    for pa, pb in zip(leagues[0]['players'], leagues[1]['players']):
        assert([f.name for f in pa.friends] == [f.name for f in pb.friends])
        assert([a.name for a in pa.avoid] == [a.name for a in pb.avoid])

