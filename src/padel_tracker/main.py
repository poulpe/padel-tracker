from padel_tracker.database.db import (
    Session,
    create_db_and_tables,
    get_db_session,
)
from padel_tracker.services.player_manager import (
    create_player,
    get_player_from_name,
    create_team,
    # TeamExistsError,
    TeamNotFoundError,
    get_team_from_players_name,
    PlayerExistsError,
)
from padel_tracker.services.match_manager import create_match
from padel_tracker.utils.datetime_utils import now


def create_dummy_players(session: Session):
    try:
        create_player(session=session, name="p1", elo_rating=1000)
        create_player(session=session, name="p2", elo_rating=940, nb_matches=100)
        create_player(session=session, name="p3", elo_rating=1200)
        create_player(session=session, name="p4", elo_rating=1100, nb_matches=100)
    except PlayerExistsError:
        pass


def create_dummy_teams_and_match(session: Session):
    p1 = get_player_from_name(session, "p1")
    p2 = get_player_from_name(session, "p2")
    p3 = get_player_from_name(session, "p3")
    p4 = get_player_from_name(session, "p4")

    print(f"INIT {p1.elo_rating = }")
    print(f"INIT {p2.elo_rating = }")
    print(f"INIT {p3.elo_rating = }")
    print(f"INIT {p4.elo_rating = }")

    t1_names = ["p1", "p2"]
    try:
        t1 = get_team_from_players_name(session, *t1_names)
    except TeamNotFoundError:
        t1 = create_team(session, *t1_names)
    t2_names = ["p3", "p4"]
    try:
        t2 = get_team_from_players_name(session, *t2_names)
    except TeamNotFoundError:
        t2 = create_team(session, *t2_names)

    match = create_match(session, teams=[t1, t2], date=now(), score="6-4, 6-3")

    print(f"UPDATED {p1.elo_rating = }")
    print(f"UPDATED {p2.elo_rating = }")
    print(f"UPDATED {p3.elo_rating = }")
    print(f"UPDATED {p4.elo_rating = }")

    print(match)


if __name__ == "__main__":
    # Creation
    create_db_and_tables()

    # Create players
    with get_db_session() as session:
        create_dummy_players(session)

    # Create a match
    with get_db_session() as session:
        create_dummy_teams_and_match(session)

    print("END")
