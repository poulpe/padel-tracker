import datetime

import pytest

from padel_tracker.utils.datetime_utils import make_datetime
from padel_tracker.utils.errors import SamePlayerInBothTeamsError
from padel_tracker.models.ranking import ELO_BASE_RATING
from padel_tracker.services import player_manager, league_manager, match_manager
from tests.conftest import (
    TEST_LEAGUE_NAME,
    TEST_P1_NAME,
    TEST_P2_NAME,
    TEST_P3_NAME,
    TEST_P4_NAME,
)


def test_create_get_delete_match(
    db_session, make_dummy_league, make_dummy_player, make_dummy_team, make_dummy_match
):
    # Fetch players and teams
    league = make_dummy_league(TEST_LEAGUE_NAME)
    p1 = make_dummy_player(TEST_P1_NAME, league=league)
    p2 = make_dummy_player(TEST_P2_NAME, league=league)
    p3 = make_dummy_player(TEST_P3_NAME, league=league)
    p4 = make_dummy_player(TEST_P4_NAME, league=league)
    p1_elo_rating_before = p1.elo_rating
    p2_elo_rating_before = p2.elo_rating
    p3_elo_rating_before = p3.elo_rating
    p4_elo_rating_before = p4.elo_rating

    t1 = make_dummy_team(TEST_P1_NAME, TEST_P2_NAME, TEST_LEAGUE_NAME)
    t2 = make_dummy_team(TEST_P3_NAME, TEST_P4_NAME, TEST_LEAGUE_NAME)

    # Create match
    match = make_dummy_match(
        team1_player1_name=TEST_P1_NAME,
        team1_player2_name=TEST_P2_NAME,
        team2_player1_name=TEST_P3_NAME,
        team2_player2_name=TEST_P4_NAME,
        league_name=TEST_LEAGUE_NAME,
        date=datetime.datetime.now(),
        score="4-6, 2-6",
        is_finished=True,
        is_friendly=False,
        delete_afterwards=False,
    )
    assert match.team1_name == t1.name
    assert match.team2_name == t2.name
    winner_team, loser_team = match.get_winners_losers()
    assert match.team1_won is False
    assert winner_team == t2
    assert loser_team == t1
    ## Check elo_rating players changed
    p1 = player_manager.get_player_from_name(db_session, TEST_P1_NAME)
    p2 = player_manager.get_player_from_name(db_session, TEST_P2_NAME)
    p3 = player_manager.get_player_from_name(db_session, TEST_P3_NAME)
    p4 = player_manager.get_player_from_name(db_session, TEST_P4_NAME)
    p1_elo_rating_after = p1.elo_rating
    p2_elo_rating_after = p2.elo_rating
    p3_elo_rating_after = p3.elo_rating
    p4_elo_rating_after = p4.elo_rating

    assert p1_elo_rating_before > p1_elo_rating_after
    assert p2_elo_rating_before > p2_elo_rating_after
    assert p3_elo_rating_before < p3_elo_rating_after
    assert p4_elo_rating_before < p4_elo_rating_after

    # Delete match
    match_manager.delete_match(db_session, match_id=match.id)
    ## Check elo_rating players have been reverted
    p1 = player_manager.get_player_from_name(db_session, TEST_P1_NAME)
    p2 = player_manager.get_player_from_name(db_session, TEST_P2_NAME)
    p3 = player_manager.get_player_from_name(db_session, TEST_P3_NAME)
    p4 = player_manager.get_player_from_name(db_session, TEST_P4_NAME)
    assert p1_elo_rating_before == p1.elo_rating
    assert p2_elo_rating_before == p2.elo_rating
    assert p3_elo_rating_before == p3.elo_rating
    assert p4_elo_rating_before == p4.elo_rating


def test_create_match_same_player_both_teams(
    db_session, make_dummy_league, make_dummy_player, make_dummy_team
):
    # Make league/players
    league = make_dummy_league(TEST_LEAGUE_NAME)
    for name in [TEST_P1_NAME, TEST_P2_NAME, TEST_P3_NAME]:
        make_dummy_player(name, league=league)
    # Retrieve teams
    t1_with_p1 = make_dummy_team(
        player1_name=TEST_P1_NAME,
        player2_name=TEST_P2_NAME,
        league_name=TEST_LEAGUE_NAME,
    )
    t2_with_p1 = make_dummy_team(
        player1_name=TEST_P1_NAME,
        player2_name=TEST_P3_NAME,
        league_name=TEST_LEAGUE_NAME,
    )
    # Create match
    with pytest.raises(SamePlayerInBothTeamsError):
        match_manager.create_match(
            db_session,
            teams=[t1_with_p1, t2_with_p1],
            league_name=TEST_LEAGUE_NAME,
            date=datetime.datetime.now(),
            score="4-6, 2-6",
            is_finished=True,
        )


def test_make_dummy_match(make_dummy_match):
    # Make a date
    date = make_datetime(day=5, month=2, year=2025, hour=19, minute=30)
    # Go
    match = make_dummy_match(
        team1_player1_name="Agustin Tapas",
        team1_player2_name="Martin Di Neuneu",
        team2_player1_name="Juan Cabron",
        team2_player2_name="Ale Gralan",
        league_name="Mucho Pro League",
        date=date,
        score="6-2, 7-6",
    )
    assert match.team1_won


def test_populate_db(db_session, populate_db):
    # Populate db
    league_name = "Ultra Liga"
    player_names = [
        "Agustin Tapas",
        "Martin Di Neuneu",
        "Juan Cabron",
        "Alejandro Gralan",
        "Arturo Coño",
        "Juan Trellent",
        "Federico Zigotto",
        "Franco Chupachups",
    ]
    nb_matches = 3
    populate_db(league_name, player_names, nb_matches=nb_matches)
    # Check league has been updated
    league = league_manager.get_league_from_name(db_session, league_name)
    assert league.nb_matches == nb_matches
    assert league.nb_players == len(player_names)
    # Check some Elo rankings have changed
    df_players = player_manager.get_all_players_from_league(
        session=db_session,
        as_df=True,
        league_name=league.name,
    )
    df_players = df_players.sort_values("elo_rating", ascending=False).reset_index()
    assert df_players.at[0, "elo_rating"] > ELO_BASE_RATING  # 1st player
    assert df_players.at[len(player_names) - 1, "elo_rating"] < ELO_BASE_RATING  # Last
