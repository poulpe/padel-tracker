"""
Populate db with previous data from my history on PadelID
"""

import logging

from padel_tracker.utils.logs import DEFAULT_LOG_FORMATTER
from padel_tracker.utils.errors import PlayerExistsError, LeagueExistsError
from padel_tracker.utils.datetime_utils import make_datetime
from padel_tracker.database.db import Session, DB
from padel_tracker.services import (
    player_manager,
    match_manager,
    league_manager,
)
from padel_tracker.main import init_app

LOG_LEVEL = "DEBUG"
LOGGER = logging.getLogger("populate_db_history")
LOGGER.setLevel(LOG_LEVEL)
LOG_HANDLER = logging.StreamHandler()
LOG_HANDLER.setLevel(LOG_LEVEL)
LOG_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)
LOGGER.addHandler(LOG_HANDLER)

# fmt: off
list_match_data = [
    {"day":3, "month":10, "year": 2024,  "hour":18, "t1_names":["ElTrueno","LaBiba"], "t2_names":["Raqueta Loca","Chaco Smash"], "score":"7-6"},
    {"day":17, "month":10, "year": 2024, "hour":18, "t1_names":["ElTrueno","Raqueta Loca"], "t2_names":["Chaco Smash","LaBiba"], "score":"6-3, 6-3"},
    {"day":22, "month":10, "year": 2024, "hour":18, "t1_names":["ElTrueno","Raqueta Loca"], "t2_names":["Chaco Smash","LaBiba"], "score":"4-6, 6-4, 6-1"},
    {"day":7, "month":11, "year": 2024,  "hour":18, "t1_names":["ElTrueno","LaBiba"], "t2_names":["Raqueta Loca","Chaco Smash"], "score":"3-6"},
    {"day":7, "month":11, "year": 2024,  "hour":19, "t1_names":["LaBiba","Chaco Smash"], "t2_names":["ElTrueno","Raqueta Loca"], "score":"6-7"},
    {"day":12, "month":11, "year": 2024, "hour":18, "t1_names":["ElTrueno","Manu Revés"], "t2_names":["Chaco Smash","LaBiba"], "score":"2-6"},
    {"day":29, "month":11, "year": 2024, "hour":18, "t1_names":["ElTrueno","Raqueta Loca"], "t2_names":["Chaco Smash","LaBiba"], "score":"6-2"},
    {"day":29, "month":11, "year": 2024, "hour":19, "t1_names":["ElTrueno","LaBiba"], "t2_names":["Chaco Smash","Raqueta Loca"], "score":"7-6"},
    {"day":7, "month":1, "year": 2025,   "hour":18, "t1_names":["ElTrueno","Raqueta Loca"], "t2_names":["Chaco Smash","LaBiba"], "score":"6-4, 6-2"},
    {"day":14, "month":1, "year": 2025,  "hour":18, "t1_names":["ElTrueno","Raqueta Loca"], "t2_names":["Chaco Smash","LaBiba"], "score":"6-4, 6-2"},
    {"day":28, "month":1, "year": 2025,  "hour":18, "t1_names":["ElTrueno","Raqueta Loca"], "t2_names":["Chaco Smash","LaBiba"], "score":"6-1"},
    {"day":28, "month":1, "year": 2025,  "hour":19, "t1_names":["ElTrueno","LaBiba"], "t2_names":["Chaco Smash","Raqueta Loca"], "score":"4-6"},
    {"day":5, "month":2, "year": 2025,  "hour":19, "t1_names":["ElTrueno","LaBiba"], "t2_names":["Chaco Smash","Raqueta Loca"], "score":"7-6,6-2"},
]
# fmt: on

LEAGUE_MAIN = "Liga Demo"


def create_league(session: Session):
    try:
        league_manager.create_league(
            session=session,
            name=LEAGUE_MAIN,
            description="Just for fun",
        )
    except LeagueExistsError:
        pass


def create_players(session: Session):
    main_league = league_manager.get_league_from_name(session=session, name=LEAGUE_MAIN)
    for player_name in [
        "ElTrueno",
        "Chaco Smash",
        "Raqueta Loca",
        "LaBiba",
        "Manu Revés",
    ]:
        try:
            player_manager.create_player(
                session=session, name=player_name, league=main_league
            )
        except PlayerExistsError:
            LOGGER.info(f"Player {player_name} already exists, skip creation")


def create_matches(session: Session, list_match_data, league_name: str):
    for match_data in list_match_data:
        t1_names = match_data["t1_names"]
        t2_names = match_data["t2_names"]
        t1 = player_manager.get_team_from_players_name(
            session, *t1_names, league_name=league_name, create_if_not_found=True
        )
        t2 = player_manager.get_team_from_players_name(
            session, *t2_names, league_name=league_name, create_if_not_found=True
        )

        match_date = make_datetime(
            match_data["day"],
            match_data["month"],
            match_data["year"],
            match_data["hour"],
        )
        match = match_manager.create_match(
            session,
            teams=[t1, t2],
            league_name=league_name,
            date=match_date,
            score=match_data["score"],
        )
        LOGGER.info(f"create_matches: successfully created match (id = {match.id})")


if __name__ == "__main__":
    init_app()

    # Populate leagues
    with DB.get_session() as session:
        create_league(session)
        create_players(session)

    # Populates matches
    with DB.get_session() as session:
        create_matches(
            session=session, list_match_data=list_match_data, league_name=LEAGUE_MAIN
        )

    LOGGER.warning("END")
