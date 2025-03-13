import pytest

from padel_tracker.utils.errors import PlayerExistsError
from padel_tracker.services.player_manager import (
    create_player,
    get_player_from_name,
    delete_player,
)


def test_create_get_delete_player(db_session):
    # Create
    player_name = "CrashTest Player"
    player = create_player(db_session, name=player_name)
    assert player.name == player_name
    assert player.elo_rating > 0
    # Get
    found_player = get_player_from_name(db_session, player_name)
    assert found_player is not None
    assert found_player.name == player_name
    # Delete
    delete_player(db_session, player_name)


def test_create_existing_player(db_session):
    # Ensure player is created
    player_name = "Alreadythere Player"
    try:
        player = create_player(db_session, name=player_name)
        assert player.name == player_name
        assert player.elo_rating > 0
    except PlayerExistsError:
        pass
    # Check raising an error when recreating it
    with pytest.raises(PlayerExistsError):
        player = create_player(db_session, name=player_name)
