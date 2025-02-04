"""
Populate db with previous data from my history on PadelID
"""

import logging

from padel_tracker.utils.logs import DEFAULT_LOG_FORMATTER
from padel_tracker.utils.errors import PlayerExistsError, LeagueExistsError
from padel_tracker.utils.datetime_utils import make_datetime
from padel_tracker.database.db import Session, DB
from padel_tracker.services import player_manager, match_manager, league_manager
from padel_tracker.main import init_app

LOG_LEVEL = "INFO"
LOGGER = logging.getLogger("populate_db_history")
LOGGER.setLevel(LOG_LEVEL)
LOG_HANDLER = logging.StreamHandler()
LOG_HANDLER.setLevel(LOG_LEVEL)
LOG_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)
LOGGER.addHandler(LOG_HANDLER)

# fmt: off
list_match_data = [
    {"day":3, "month":10, "year": 2024,  "hour":18, "t1_names":["ElPoulpo","Biboono"], "t2_names":["Sergissimo","Maximator"], "score":"7-6"},
    {"day":17, "month":10, "year": 2024, "hour":18, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-3, 6-3"},
    {"day":22, "month":10, "year": 2024, "hour":18, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"4-6, 6-4, 6-1"},
    {"day":7, "month":11, "year": 2024,  "hour":18, "t1_names":["ElPoulpo","Biboono"], "t2_names":["Sergissimo","Maximator"], "score":"3-6"},
    {"day":7, "month":11, "year": 2024,  "hour":19, "t1_names":["Biboono","Maximator"], "t2_names":["ElPoulpo","Sergissimo"], "score":"6-7"},
    {"day":12, "month":11, "year": 2024, "hour":18, "t1_names":["ElPoulpo","Axelito"], "t2_names":["Maximator","Biboono"], "score":"2-6"},
    {"day":29, "month":11, "year": 2024, "hour":18, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-2"},
    {"day":29, "month":11, "year": 2024, "hour":19, "t1_names":["ElPoulpo","Biboono"], "t2_names":["Maximator","Sergissimo"], "score":"7-6"},
    {"day":7, "month":1, "year": 2025,   "hour":18, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-4, 6-2"},
    {"day":14, "month":1, "year": 2025,  "hour":18, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-4, 6-2"},
    {"day":28, "month":1, "year": 2025,  "hour":18, "t1_names":["ElPoulpo","Sergissimo"], "t2_names":["Maximator","Biboono"], "score":"6-1"},
    {"day":28, "month":1, "year": 2025,  "hour":19, "t1_names":["ElPoulpo","Biboono"], "t2_names":["Maximator","Sergissimo"], "score":"4-6"},
]
# fmt: on

LEAGUE_MAIN = "Ligue des pédales du Padel"
# LEAGUE_ALT = "Liga Delabita"


def create_league(session: Session):
    for league_name in [LEAGUE_MAIN]:  # , LEAGUE_ALT]:
        try:
            league_manager.create_league(session=session, name=league_name)
        except LeagueExistsError:
            pass


def create_players(session: Session):
    main_league = league_manager.get_league_from_name(session=session, name=LEAGUE_MAIN)
    for player_name in ["ElPoulpo", "Maximator", "Sergissimo", "Biboono", "Axelito"]:
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


# def assign_leagues(session: Session):
#     # Assign someone to LEAGUE_ALT
#     try:
#         player = player_manager.get_player_from_name(session=session, name="Maximator")
#         league = league_manager.get_league_from_name(session=session, name=LEAGUE_ALT)
#         link = LinkPlayerLeague(
#             player=player,
#             league=league,
#             player_name=player.name,
#             league_name=league.name,
#         )
#         commit_to_db(link, session=session)
#     except:
#         LOGGER.warning("league link already exists")

# def trial_get_all_players_from_league(session):
#     return player_manager.get_all_players_from_league(
#         session=session, league_name=LEAGUE_MAIN
#     )
#
#
# def trial_get_all_teams_from_league(session):
#     return player_manager.get_all_teams_from_league(
#         session=session, league_name=LEAGUE_MAIN
#     )


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

    # # Trial: Delete match
    # with DB.get_session() as session:
    #     match_manager.delete_match(
    #         session=session, match_id="9d7aae10582e495c97280c2fb0c1abf4"
    #     )

    # # Trial: Show leagues
    # with DB.get_session():
    #     main_league = league_manager.get_league_from_name(session=session, name="Ligue des pédales du Padel")
    #     list_player_names = [link.player.name for link in main_league.player_links]
    #     print(list_player_names)
    #     print("coucou")
    #     league = league_manager.get_league_from_name(session=session, name="Liga Delabita")
    #     list_player_names = [link.player.name for link in league.player_links]
    #     print(list_player_names)
    #     yes = trial_get_all_players_from_league(session)
    #     print(yes)

    # # Trial: Show teams
    # with DB.get_session() as session:
    #     yes = trial_get_all_teams_from_league(session)
    #     print(yes)
    # with DB.get_session() as session:
    #     df = ranking_manager.get_all_elo_rating_histories_from_players_in_league(session=session, league_name=LEAGUE_MAIN,as_df=True)

    LOGGER.warning("END")
