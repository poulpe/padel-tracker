"""
Script to launch "Season reset" for the Elo ratings on the database
Typically to be triggered each years via schedule Github actions/workflows

Will rely on having :
- secrets and conf passed as environment variables via the Github action "env" section and secrets management
- or because a .env file is exsiting with the proper secrets and configuration, typically when launching it from local
"""

import re

from padel_tracker.database.db import DB
from padel_tracker.services import event_manager, ranking_manager


def deduct_next_season_name(name: str) -> str:
    """Increment numbers in a string by 1
    Examples
    --------
    >>> deduct_next_season_name("S2")
    'S3'
    >>> deduct_next_season_name("Season 2024-2025")
    'Season 2025-2026'
    """
    return re.sub(r"\d+", lambda x: str(int(x.group()) + 1), name)


if __name__ == "__main__":
    with DB.get_session() as session:
        # Deduct new season_name
        last_reset_event = event_manager.get_last_season_reset_event(session)
        new_season_name = deduct_next_season_name(last_reset_event.name)
        # Launch API call
        ranking_manager.apply_season_reset_to_all_players(
            session=session,
            season_name=new_season_name,
            event_description=f"{new_season_name} reset",
        )
