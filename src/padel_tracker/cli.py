import typer

from padel_tracker.database.db import DB
from padel_tracker.services import player_manager, league_manager, ranking_manager

# Declare CLI Typer app
app = typer.Typer()
leagues_app = typer.Typer(help="CRUD on Leagues")
players_app = typer.Typer(help="CRUD on Players and Teams")
ranking_app = typer.Typer(help="Rank and Elo rating related commands")
app.add_typer(leagues_app, name="leagues")
app.add_typer(players_app, name="players")
app.add_typer(ranking_app, name="ranking")


# Leagues related
@leagues_app.command("list")
def get_all_leagues():
    """Print all leagues in database"""
    with DB.get_session() as session:
        all_leagues = league_manager.get_all_leagues(session=session)
    print(*all_leagues, sep="\n")


# Players related
@players_app.command("rename")
def rename_player(current_name: str, new_name: str):
    with DB.get_session() as session:
        player_manager.rename_player(
            session=session, current_name=current_name, new_name=new_name
        )


@players_app.command("delete")
def delete_player(name: str):
    with DB.get_session() as session:
        player_manager.delete_player(session=session, name=name)


# Ranking related
@ranking_app.command("update")
def update_players_rank(force: bool = False):
    """
    Updates players ranking in all leagues if a matched occurred since last update
    (except if "force")

    Parameters
    ----------
    force: bool, optional
        Apply ranking update even if no matches played in between. Default is False.
    """
    with DB.get_session() as session:
        all_leagues = league_manager.get_all_leagues(session)
        for league in all_leagues:
            is_update_needed = False
            if not force:
                # Check if any match since last ranking update
                try:
                    last_rank_hist = ranking_manager.get_last_rank_history_from_league(
                        session=session, league_id=league.id
                    )
                    is_update_needed = league.last_match_date > last_rank_hist.date
                except (KeyError, IndexError):
                    pass  # Means no match in league
            if is_update_needed or force:
                ranking_manager.update_players_rank(
                    league_name=league.name, league_id=league.id, session=session
                )


if __name__ == "__main__":
    app()
