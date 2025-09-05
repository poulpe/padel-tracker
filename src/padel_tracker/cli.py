from typing_extensions import Annotated
import subprocess

import typer

from padel_tracker.utils.paths import APP_PATH
from padel_tracker.utils.conf import get_conf_message
from padel_tracker.database.db import DB
from padel_tracker.services import (
    player_manager,
    league_manager,
    ranking_manager,
    user_manager,
)

# Declare CLI Typer app
## Subapps
leagues_app = typer.Typer(help="CRUD on Leagues")
leagues_admin_app = typer.Typer(help="For league administrator related commands")
leagues_app.add_typer(leagues_admin_app, name="admin")
players_app = typer.Typer(help="CRUD on Players and Teams")
ranking_app = typer.Typer(help="Rank and Elo rating related commands")
## Main app
app = typer.Typer(no_args_is_help=True)
app.add_typer(leagues_app, name="leagues")
app.add_typer(players_app, name="players")
app.add_typer(ranking_app, name="ranking")


# Leagues related
@leagues_app.command("list")
def list_all_leagues():
    """Print all leagues in database"""
    with DB.get_session() as session:
        all_leagues = league_manager.get_all_leagues(session=session)
    for league in all_leagues:
        print(repr(league))


@leagues_app.command("delete")
def delete_league(name: str):
    """Delete a league and all associated matches"""
    with DB.get_session() as session:
        league_manager.delete_league(session=session, name=name)


@leagues_admin_app.command("list")
def list_league_admins(league_name: str):
    """Show list of administrator in given league name"""
    with DB.get_session() as session:
        admins = league_manager.get_admin_names_from_league_name(session, league_name)
    for admin in admins:
        print(repr(admin))


@leagues_admin_app.command("assign")
def assign_league_admins(league_name: str, user_name: str):
    """Assign 'user_name' as admin of 'league_name'"""
    with DB.get_session() as session:
        league = league_manager.get_league_from_name(session, league_name)
        user = user_manager.get_user_from_name(session, user_name)
        league_manager.assign_admin_to_league(session, user, league)


# Players related
@players_app.command("rename")
def rename_player(current_name: str, new_name: str):
    """Rename a player to another valid 'new_name'"""
    with DB.get_session() as session:
        player_manager.rename_player(
            session=session, current_name=current_name, new_name=new_name
        )


@players_app.command("delete")
def delete_player(name: str):
    """Delete a player"""
    with DB.get_session() as session:
        player_manager.delete_player(session=session, name=name)


@players_app.command("list")
def list_players(
    league_name: Annotated[str, typer.Argument()] = "",
    all: Annotated[
        bool, typer.Option(help="Show all players from all leagues")
    ] = False,
):
    """List players from given 'league_name' in database, or from all leagues if --all"""
    if all and league_name:
        raise typer.BadParameter("can't use --all and specify league at the same time")

    with DB.get_session() as session:
        if all:
            players = player_manager.get_all_players(session)
        elif league_name:
            players = player_manager.get_all_players_from_league(session, league_name)
        else:
            raise typer.BadParameter("provide a `league_name` or use --all")

    for player in players:
        print(repr(player))


# Ranking related
@ranking_app.command("update")
def update_players_rank(
    force: Annotated[
        bool,
        typer.Option(help="Apply ranking update even if no matches played in between"),
    ] = False,
):
    """Updates players ranking in all leagues if a matched occurred since last update"""
    with DB.get_session() as session:
        all_leagues = league_manager.get_all_leagues(session)
        for league in all_leagues:
            is_update_needed = False
            if not force:
                # Check if any match since last ranking update
                try:
                    last_rank_hist = ranking_manager.get_last_rank_history_from_league(
                        session=session, league_name=league.name
                    )
                    is_update_needed = league.last_match_date > last_rank_hist.date
                except (KeyError, IndexError):
                    pass  # Means no match in league
            if is_update_needed or force:
                ranking_manager.update_players_rank(
                    league_name=league.name, league_id=league.id, session=session
                )


# App related
@app.command("ui")
def run_streamlit_app():
    """Open the Streamlit UI in the web browser"""
    subprocess.run(["streamlit", "run", APP_PATH])


@app.command("conf")
def show_conf():
    """Display read configuration in .env and .secrets.toml"""
    print(get_conf_message())


if __name__ == "__main__":
    app()
