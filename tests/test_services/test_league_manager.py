from padel_tracker.services.league_manager import (
    create_league,
    get_league_from_name,
    delete_league,
)


def test_create_get_delete_league(db_session):
    league_name = "CrashTest League"
    # Create
    league = create_league(db_session, name=league_name, is_private=True)
    assert league.name == league_name
    assert league.is_private is True
    assert league.nb_matches == 0
    assert league.nb_players == 0
    # Get
    found_league = get_league_from_name(db_session, league_name)
    assert found_league is not None
    assert found_league.name == league_name
    # Delete
    delete_league(db_session, league_name)
