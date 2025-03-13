from uuid import uuid4
from datetime import datetime
from padel_tracker.models.players import Player, EloRatingHistory
from padel_tracker.models.ranking import ELO_BASE_RATING


def test_create_player():
    player = Player(name="Coucou")
    assert player.name == "Coucou"
    assert player.id is not None
    assert player.nb_matches == 0
    assert player.nb_victories == 0
    assert player.nb_defeats == 0
    assert player.elo_rating == ELO_BASE_RATING
    player.elo_rating = 1200


def test_elo_rating_history():
    player_id = uuid4()
    history = EloRatingHistory(
        player_id=player_id,
        player_name="John Doe",
        elo_rating=1200,
        elo_rating_gain=50,
        date=datetime.now(),
    )
    assert history.player_id == player_id
    assert history.player_name == "John Doe"
    assert history.elo_rating == 1200
    assert history.elo_rating_gain == 50
