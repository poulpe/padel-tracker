import datetime

import pytest

from tests.conftest import (
    TEST_LEAGUE_NAME,
    TEST_P1_NAME,
    TEST_P2_NAME,
    TEST_P3_NAME,
    TEST_P4_NAME,
)
from padel_tracker.utils.errors import (
    SamePlayerInOneTeamError,
    SamePlayerInBothTeamsError,
    LeagueNotFoundError,
    PlayerExistsError,
)
from padel_tracker.services.player_manager import (
    create_player,
    get_player_from_name,
    get_team_from_players_name,
)
from padel_tracker.services.league_manager import create_league, get_league_from_name
from padel_tracker.services.match_manager import create_match, delete_match


def test_create_get_delete_match(db_session):
    # Retrieve players and team
    ## Ensure league and players are created
    try:
        test_league = get_league_from_name(session=db_session, name=TEST_LEAGUE_NAME)
    except LeagueNotFoundError:
        test_league = create_league(db_session, name=TEST_LEAGUE_NAME, is_private=False)
    for player_name in [TEST_P1_NAME, TEST_P2_NAME, TEST_P3_NAME, TEST_P4_NAME]:
        try:
            create_player(db_session, name=player_name, league=test_league)
        except PlayerExistsError:
            pass
    ## Fetch them
    p1 = get_player_from_name(db_session, TEST_P1_NAME)
    p2 = get_player_from_name(db_session, TEST_P2_NAME)
    p3 = get_player_from_name(db_session, TEST_P3_NAME)
    p4 = get_player_from_name(db_session, TEST_P4_NAME)
    p1_elo_rating_before = p1.elo_rating
    p2_elo_rating_before = p2.elo_rating
    p3_elo_rating_before = p3.elo_rating
    p4_elo_rating_before = p4.elo_rating

    t1 = get_team_from_players_name(
        db_session,
        player1_name=TEST_P1_NAME,
        player2_name=TEST_P2_NAME,
        league_name=TEST_LEAGUE_NAME,
        create_if_not_found=True,
    )
    t2 = get_team_from_players_name(
        db_session,
        player1_name=TEST_P3_NAME,
        player2_name=TEST_P4_NAME,
        league_name=TEST_LEAGUE_NAME,
        create_if_not_found=True,
    )

    # Create match
    match = create_match(
        db_session,
        teams=[t1, t2],
        league_name=TEST_LEAGUE_NAME,
        date=datetime.datetime.now(),
        score="4-6, 2-6",
        is_finished=True,
    )
    assert match.team1_name == t1.name
    assert match.team2_name == t2.name
    winner_team, loser_team = match.get_winners_losers()
    assert match.team1_won is False
    assert winner_team == t2
    assert loser_team == t1
    ## Check elo_rating players changed
    p1 = get_player_from_name(db_session, TEST_P1_NAME)
    p2 = get_player_from_name(db_session, TEST_P2_NAME)
    p3 = get_player_from_name(db_session, TEST_P3_NAME)
    p4 = get_player_from_name(db_session, TEST_P4_NAME)
    p1_elo_rating_after = p1.elo_rating
    p2_elo_rating_after = p2.elo_rating
    p3_elo_rating_after = p3.elo_rating
    p4_elo_rating_after = p4.elo_rating

    assert p1_elo_rating_before > p1_elo_rating_after
    assert p2_elo_rating_before > p2_elo_rating_after
    assert p3_elo_rating_before < p3_elo_rating_after
    assert p4_elo_rating_before < p4_elo_rating_after

    # Delete match
    delete_match(db_session, match_id=match.id)
    ## Check elo_rating players have been reverted
    p1 = get_player_from_name(db_session, TEST_P1_NAME)
    p2 = get_player_from_name(db_session, TEST_P2_NAME)
    p3 = get_player_from_name(db_session, TEST_P3_NAME)
    p4 = get_player_from_name(db_session, TEST_P4_NAME)
    assert p1_elo_rating_before == p1.elo_rating
    assert p2_elo_rating_before == p2.elo_rating
    assert p3_elo_rating_before == p3.elo_rating
    assert p4_elo_rating_before == p4.elo_rating


def test_create_match_same_player_both_teams(db_session):
    # Check cannot create team of one player
    with pytest.raises(SamePlayerInOneTeamError):
        get_team_from_players_name(
            db_session, player1_name=TEST_P1_NAME, player2_name=TEST_P1_NAME
        )
    # Retrieve teams
    t1_with_p1 = get_team_from_players_name(
        db_session,
        player1_name=TEST_P1_NAME,
        player2_name=TEST_P2_NAME,
        league_name=TEST_LEAGUE_NAME,
        create_if_not_found=True,
    )
    t2_with_p1 = get_team_from_players_name(
        db_session,
        player1_name=TEST_P1_NAME,
        player2_name=TEST_P3_NAME,
        league_name=TEST_LEAGUE_NAME,
        create_if_not_found=True,
    )
    # Create match
    with pytest.raises(SamePlayerInBothTeamsError):
        create_match(
            db_session,
            teams=[t1_with_p1, t2_with_p1],
            league_name=TEST_LEAGUE_NAME,
            date=datetime.datetime.now(),
            score="4-6, 2-6",
            is_finished=True,
        )
