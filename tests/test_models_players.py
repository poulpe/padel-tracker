from padel_tracker.models.players import Player


def test_player_creation():
    yes = Player(name="Coucou")
    assert yes.name == "Coucou"
    assert yes.id is not None
    assert yes.nb_matches == 0
    yes.elo_rating = 1200


def test_team_creation():
    pass
