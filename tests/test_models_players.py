from time import sleep

# from uuid import uuid4
#
# import pytest

from padel_tracker.models.players import Player


def test_player_creation():
    yes = Player(name="Coucou")
    print(yes)
    sleep(0.5)
    yes.elo_rating = 1200
    print(yes.id)


def test_team_creation():
    pass
