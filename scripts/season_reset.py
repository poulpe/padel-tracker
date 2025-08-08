"""
Script to launch "Season reset" for the Elo ratings on the database
Typically to be triggered each years via schedule Github actions/workflows

Will rely on having :
- secrets and conf passed as environment variables via the Github action "env" section and secrets management
- or because a .env file is exsiting with the proper secrets and configuration, typically for launching it from local
"""

# TODO (prio 1) : make season_reset script

from padel_tracker.database.db import DB
from padel_tracker.utils.datetime_utils import now
from padel_tracker.services import event_manager  # ranking_manager

# Deduct new season_name
## i.e : fetch last "season reset" event, read event.name and increment
season_name = "S2"

# Launch API call
with DB.get_session() as session:
    # ranking_manager.apply_season_reset_to_all_players(
    #     session=session,
    #     season_name=season_name,
    #     event_description=f"{season_name} reset",
    # )
    event_manager.create_event(
        session=session, name=f"test creation {season_name=}", date=now()
    )
