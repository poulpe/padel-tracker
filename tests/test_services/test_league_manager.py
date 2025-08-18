import pytest

from padel_tracker.utils.errors import LeagueNotFoundError
from padel_tracker.services import league_manager


def test_create_get_delete_league(db_session, make_dummy_league):
    league_name = "CrashTest League"
    # Create
    league = make_dummy_league(name=league_name, is_private=True)
    assert league.name == league_name
    assert league.is_private is True
    assert league.nb_matches == 0
    assert league.nb_players == 0
    # Get
    found_league = league_manager.get_league_from_name(db_session, league_name)
    assert found_league is not None
    assert found_league.name == league_name
    # Delete is done in the teardown of 'make_dummy_league' fixture


def test_delete_unexisting_league(db_session):
    with pytest.raises(LeagueNotFoundError):
        league_manager.delete_league(db_session, "Nope this league is not real")


def test_add_player_to_league(
    db_session, make_dummy_user, make_dummy_player, make_dummy_league
):
    # Create admin user/player of league #1
    admin1_name = "Le chef"
    make_dummy_user(name=admin1_name, is_create_player=True)
    # Create league #1
    league1_name = "Super cool league"
    league1 = make_dummy_league(
        name=league1_name, is_private=True, admin_name=admin1_name
    )

    # Create admin player of league #2
    admin2_name = "Bof le chef"
    make_dummy_user(name=admin2_name, is_create_player=True)
    # Create league #2
    league2_name = "Less cool league"
    league2 = make_dummy_league(
        name=league2_name, is_private=True, admin_name=admin2_name
    )

    # Create players in league #1 and league #2
    player2_name = "Follower Dos"
    player3_name = "Follower Tres"
    player4_name = "Follower Cuatro"
    for name in [player2_name, player3_name, player4_name]:
        make_dummy_player(name=name, league=[league1, league2])

    # Check players in league #1
    list_links_league1 = league_manager.get_linkplayerleague_from_league(
        db_session, league1_name
    )
    list_player_names_league1 = [link.player_name for link in list_links_league1]
    for player_name in [admin1_name, player2_name, player3_name, player4_name]:
        assert player_name in list_player_names_league1

    # Check players in league #2
    list_links_league2 = league_manager.get_linkplayerleague_from_league(
        db_session, league2_name
    )
    list_player_names_league2 = [link.player_name for link in list_links_league2]
    for player_name in [admin2_name, player2_name, player3_name, player4_name]:
        assert player_name in list_player_names_league2

    # No needs to delete and clean, already managed by fixtures
