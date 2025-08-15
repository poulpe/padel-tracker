import pytest

from padel_tracker.database.db import commit_to_db
from padel_tracker.utils.errors import PlayerExistsError, PlayerNotFoundError
from padel_tracker.services import player_manager


def test_create_get_delete_player(db_session):
    # Create
    player_name = "CrashTest Player"
    player = player_manager.create_player(db_session, name=player_name)
    assert player.name == player_name
    assert player.elo_rating > 0
    # Get
    found_player = player_manager.get_player_from_name(db_session, player_name)
    assert found_player is not None
    assert found_player.name == player_name
    # Delete
    player_manager.delete_player(db_session, player_name)


def test_create_existing_player(db_session):
    # Ensure player is created
    player_name = "Alreadythere Player"
    try:
        player = player_manager.create_player(db_session, name=player_name)
        assert player.name == player_name
        assert player.elo_rating > 0
    except PlayerExistsError:
        pass
    # Check raising an error when recreating it
    with pytest.raises(PlayerExistsError):
        player_manager.create_player(db_session, name=player_name)


def test_delete_unexisting_player(db_session):
    with pytest.raises(PlayerNotFoundError):
        player_manager.delete_player(db_session, name="Nope SureNotExists")


def test_rename_player(db_session):
    lame_player_name = "Thisname Sucks"
    new_awesome_name = "RoxXorz Smashorz"
    # Create
    ## Ensure it doesn't exist
    try:
        player_manager.delete_player(db_session, name=lame_player_name)
    except PlayerNotFoundError:
        pass
    ## Create and make him play a bit
    player = player_manager.create_player(db_session, name=lame_player_name)
    player.nb_matches = 12
    player.nb_defeats = 10
    player.nb_victories = 2
    commit_to_db(player, session=db_session)

    # Rename
    player_manager.rename_player(
        db_session, current_name=lame_player_name, new_name=new_awesome_name
    )
    ## Ensure previous name cannot be found
    with pytest.raises(PlayerNotFoundError):
        player_manager.get_player_from_name(db_session, lame_player_name)
    ## Ensure stats are still the same
    player = player_manager.get_player_from_name(db_session, new_awesome_name)
    assert player.name == new_awesome_name
    assert player.nb_matches == 12
    assert player.nb_defeats == 10
    assert player.nb_victories == 2

    # Delete it
    player_manager.delete_player(db_session, new_awesome_name)


def test_make_dummy_player(make_dummy_player, make_dummy_league):
    my_league = make_dummy_league("ZeLeague")
    name = "Alfred"
    player = make_dummy_player(name, league=my_league)
    assert player.name == name


def test_make_dummy_team(make_dummy_team, make_dummy_player, make_dummy_league):
    p1_name = "Oui"
    p2_name = "Muchacho"
    league_name = "Daliga"
    # Ensure league and players exists
    make_dummy_league(league_name)
    make_dummy_player(p1_name)
    make_dummy_player(p2_name)
    # Go
    team = make_dummy_team(p1_name, p2_name, league_name=league_name)
    assert p1_name in team.name
