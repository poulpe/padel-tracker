from uuid import uuid4
from padel_tracker.models.leagues import League


def test_create_league():
    league = League(name="Padel League")
    assert league.name == "Padel League"
    assert league.is_private is False
    assert league.nb_matches == 0
    assert league.nb_players == 0


def test_league_uuid():
    league = League(name="Test League")
    assert isinstance(league.id, uuid4().__class__)
