"""
Populate db with previous data from my history on PadelID
"""

from padel_tracker.utils.logs import get_logger
from padel_tracker.database.db import (
    Session,
    create_db_and_tables,
    get_db_session,
)
from padel_tracker.services.player_manager import (
    create_player,
    get_team_from_players_name,
    PlayerExistsError,
)
from padel_tracker.services.match_manager import create_match
from padel_tracker.utils.datetime_utils import make_datetime

LOGGER = get_logger("script.populate_db_history", log_level="INFO")

# fmt: off
list_match_data = [
    {"day":3, "month":10, "year": 2024, "t1_names":["ElPoulpo","Biboono"], "t2_names":["Sergissimo","Maximator"], "score":"7-6"},
    {"day":17, "month":10, "year": 2024, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-3, 6-3"},
    {"day":22, "month":10, "year": 2024, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"4-6, 6-4, 6-1"},
    {"day":7, "month":11, "year": 2024, "t1_names":["ElPoulpo","Biboono"], "t2_names":["Sergissimo","Maximator"], "score":"3-6"},
    {"day":7, "month":11, "year": 2024, "t1_names":["Biboono","Maximator"], "t2_names":["ElPoulpo","Sergissimo"], "score":"6-7"},
    {"day":12, "month":11, "year": 2024, "t1_names":["ElPoulpo","Axelito"], "t2_names":["Maximator","Biboono"], "score":"2-6"},
    {"day":29, "month":11, "year": 2024, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-2"},
    {"day":29, "month":11, "year": 2024, "t1_names":["ElPoulpo","Biboono"], "t2_names":["Maximator","Sergissimo"], "score":"7-6"},
    {"day":7, "month":1, "year": 2025, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-4, 6-2"},
    {"day":14, "month":1, "year": 2025, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-4, 6-2"},
]
# fmt: on


def create_players(session: Session):
    for player_name in ["ElPoulpo", "Maximator", "Sergissimo", "Biboono", "Axelito"]:
        try:
            create_player(session=session, name=player_name)
        except PlayerExistsError:
            LOGGER.info(f"Player {player_name} already exists, skip creation")


def create_matches(session: Session, list_match_data):
    for match_data in list_match_data:
        t1_names = match_data["t1_names"]
        t2_names = match_data["t2_names"]
        t1 = get_team_from_players_name(session, *t1_names, create_if_not_found=True)
        t2 = get_team_from_players_name(session, *t2_names, create_if_not_found=True)

        match_date = make_datetime(
            match_data["day"], match_data["month"], match_data["year"]
        )
        match = create_match(
            session, teams=[t1, t2], date=match_date, score=match_data["score"]
        )
        LOGGER.info(f"create_matches: successfully created match (id = {match.id})")


if __name__ == "__main__":
    # Creation
    create_db_and_tables()

    # Populate players
    with get_db_session() as session:
        create_players(session)

    # Populates matches
    with get_db_session() as session:
        create_matches(session, list_match_data)

    LOGGER.warning("END")
