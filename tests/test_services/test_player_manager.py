import pytest
from uuid import uuid4

from padel_tracker.utils.errors import (
    PlayerExistsError,
    PlayerNotFoundError,
    SamePlayerInOneTeamError,
)
from padel_tracker.services import player_manager


def test_create_get_delete_player_no_league(db_session, make_dummy_player):
    # Create
    player_name = "CrashTest Player"
    player = make_dummy_player(name=player_name)
    assert player.name == player_name
    assert player.elo_rating > 0
    # Get
    found_player = player_manager.get_player_from_name(db_session, player_name)
    assert found_player is not None
    assert found_player.name == player_name
    # Check raising an error when recreating it
    with pytest.raises(PlayerExistsError):
        player_manager.create_player(db_session, name=player_name)
    # Delete is done in the teardown of 'make_dummy_player' fixture


def test_unexisting_player(db_session):
    with pytest.raises(PlayerNotFoundError):
        player_manager.delete_player(db_session, name="Nope SureNotExists")
    with pytest.raises(PlayerNotFoundError):
        player_manager.get_player_from_id(db_session, id=uuid4())


def test_rename_player(db_session, make_dummy_player, populate_db):
    # Prepare db
    lame_player_name = "Thisname Sucks"
    new_awesome_name = "RoxXorz Smashorz"
    populate_db(
        league_name="Lame league",
        player_names=[lame_player_name, "Lame Dos", "Lame Tres", "Lame Cuatro"],
    )
    # Store some stats before renaming player to compare afterwards
    player = make_dummy_player(name=lame_player_name)
    nb_matches_before = player.nb_matches
    nb_victories_before = player.nb_victories

    # Rename
    ## Ensure cannot rename to existing player
    with pytest.raises(PlayerExistsError):
        player_manager.rename_player(
            db_session,
            current_name=lame_player_name,
            new_name="Lame Dos",
        )
    ## Go rename
    player_manager.rename_player(
        db_session, current_name=lame_player_name, new_name=new_awesome_name
    )
    ## Ensure previous name cannot be found
    with pytest.raises(PlayerNotFoundError):
        player_manager.get_player_from_name(db_session, lame_player_name)
    ## Ensure stats are still the same
    player = player_manager.get_player_from_name(db_session, new_awesome_name)
    assert player.name == new_awesome_name
    assert player.nb_matches == nb_matches_before
    assert player.nb_victories == nb_victories_before
    # Delete is done in the teardown of 'make_dummy_player' fixture


def test_make_dummy_player_in_league(make_dummy_player, make_dummy_league):
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


def test_create_team_same_player(db_session, make_dummy_player):
    # Check cannot create team of one player
    make_dummy_player(name="Rodrigo")
    with pytest.raises(SamePlayerInOneTeamError):
        player_manager.get_team_from_players_name(
            db_session, player1_name="Rodrigo", player2_name="Rodrigo"
        )
