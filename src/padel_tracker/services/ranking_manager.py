from uuid import UUID
from datetime import datetime

import pandas as pd

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.datetime_utils import now
from padel_tracker.models.players import (
    Player,
    EloRatingHistory,
    RankHistory,
    TeamEloRatingHistory,
)
from padel_tracker.models.ranking import (
    calc_player_elo_rating_gain,
    calc_k_value,
    calc_season_reset_elo_rating_gain,
)
from padel_tracker.models.matches import Match, MatchScore
from padel_tracker.models.links import LinkPlayerLeague
from padel_tracker.models.events import EventCategory
from padel_tracker.database.db import Session, commit_to_db, read_from_db, DB
from padel_tracker.services import player_manager, event_manager

LOGGER = get_logger("ranking")


def update_players_results_after_finished_match(
    session: Session,
    match: Match,
) -> tuple[dict[str, int], dict[str, int]]:
    """Update for each players and each teams:
    - Elo ratings
    - Elo k (for players only)
    - Nb matches played, nb victories, nb defeats
    - Best Elo
    - Elo history

    Returns
    -------
    dict_elo_rating_gains: dict[str, dict[str, int]]
        Elo gains for convenience, as dict[player.name, elo_rating_gain]
    dict_updated_elo_ratings: dict[str, dict[str, int]]
        New elo for convenience, as dict[player.name, updated_elo_rating]
    """
    logger = LOGGER
    logger_debug = logger.getChild("update_players_results")
    logger_debug.debug("starting update")

    # Retrieve Match
    match.post_init()  # To write match name + validate players OK
    match_date = match.date
    winner_team, loser_team = match.get_winners_losers()
    winners: list[Player] = winner_team.players
    losers: list[Player] = loser_team.players
    logger_debug.debug("determined winners/losers")

    # Get once all current Elo
    current_elo_rating_winner_player1 = winners[0].elo_rating
    current_elo_rating_winner_player2 = winners[1].elo_rating
    current_elo_rating_loser_player1 = losers[0].elo_rating
    current_elo_rating_loser_player2 = losers[1].elo_rating
    match_score = MatchScore.from_string(match.score)
    match_score.calc_won_sets_and_games()
    nb_won_sets_diff = match_score.nb_won_sets_diff
    nb_won_games_diff = match_score.nb_won_games_diff
    logger_debug.debug("determined winners/losers")

    # Calc all new (careful not updating yet Elo, for not screwing in btw calc)
    dict_elo_rating_gains = {}

    dict_elo_rating_gains[winners[0].name] = calc_player_elo_rating_gain(
        player_elo_rating=current_elo_rating_winner_player1,
        teammate_elo_rating=current_elo_rating_winner_player2,
        opponent_player1_elo_rating=current_elo_rating_loser_player1,
        opponent_player2_elo_rating=current_elo_rating_loser_player2,
        player_nb_matches=winners[0].nb_matches,
        has_won=True,
        diff_nb_sets=nb_won_sets_diff,
        diff_nb_games=nb_won_games_diff,
    )
    dict_elo_rating_gains[winners[1].name] = calc_player_elo_rating_gain(
        player_elo_rating=current_elo_rating_winner_player2,
        teammate_elo_rating=current_elo_rating_winner_player1,
        opponent_player1_elo_rating=current_elo_rating_loser_player1,
        opponent_player2_elo_rating=current_elo_rating_loser_player2,
        player_nb_matches=winners[1].nb_matches,
        has_won=True,
        diff_nb_sets=nb_won_sets_diff,
        diff_nb_games=nb_won_games_diff,
    )
    dict_elo_rating_gains[losers[0].name] = calc_player_elo_rating_gain(
        player_elo_rating=current_elo_rating_loser_player1,
        teammate_elo_rating=current_elo_rating_loser_player2,
        opponent_player1_elo_rating=current_elo_rating_winner_player1,
        opponent_player2_elo_rating=current_elo_rating_winner_player2,
        player_nb_matches=losers[0].nb_matches,
        has_won=False,
        diff_nb_sets=nb_won_sets_diff,
        diff_nb_games=nb_won_games_diff,
    )
    dict_elo_rating_gains[losers[1].name] = calc_player_elo_rating_gain(
        player_elo_rating=current_elo_rating_loser_player2,
        teammate_elo_rating=current_elo_rating_loser_player1,
        opponent_player1_elo_rating=current_elo_rating_winner_player1,
        opponent_player2_elo_rating=current_elo_rating_winner_player2,
        player_nb_matches=losers[1].nb_matches,
        has_won=False,
        diff_nb_sets=nb_won_sets_diff,
        diff_nb_games=nb_won_games_diff,
    )
    logger_debug.debug("calculated player elo_rating gains")

    # Update players elo ratings, best Elo, nb_matches, elo k
    elo_history_entries = []
    dict_updated_elo_ratings = {}
    logger_debug.debug("starting update of player objects")
    for player in winners + losers:
        # Update player updated_date
        if not player.last_match_date or (player.last_match_date < match_date):
            player.last_match_date = match_date
        # Updated Elo
        elo_rating_gain = dict_elo_rating_gains[player.name]
        updated_elo_rating = player.elo_rating + elo_rating_gain
        player.elo_rating = updated_elo_rating
        dict_updated_elo_ratings[player.name] = updated_elo_rating
        # Best Elo
        if updated_elo_rating > player.best_elo_rating:
            player.best_elo_rating = updated_elo_rating
        # Nb matches
        player.nb_matches += 1
        # New k Elo
        player.elo_k = calc_k_value(player.nb_matches)
        # Update EloHistory (elo history only)
        player_elo_history_entry = EloRatingHistory(
            date=match_date,
            player_id=player.id,
            player_name=player.name,
            elo_rating=updated_elo_rating,
            elo_rating_gain=elo_rating_gain,
            match_id=match.id,
            match_name=match.name,
            league_id=match.league.id,
            league_name=match.league_name,
        )
        elo_history_entries.append(player_elo_history_entry)
        logger_debug.debug(f"created elo_history_entry for '{player.name}'")
    ## Update nb victory/defeat
    for player in winners:
        player.nb_victories += 1
    for player in losers:
        player.nb_defeats += 1

    # Update Team related results
    team_elo_history_entries = []
    logger_debug.debug("starting update of team objects")
    for team in [winner_team, loser_team]:
        if not team.last_match_date or (team.last_match_date < match_date):
            team.last_match_date = match_date
        # Update Team elo (will trigger comput of self.elo_rating)
        previous_elo_rating = team.elo_rating
        updated_elo_rating = team.calc_team_elo_rating()
        elo_rating_gain = updated_elo_rating - previous_elo_rating
        # Best Elo
        if updated_elo_rating > team.best_elo_rating:
            team.best_elo_rating = updated_elo_rating
        # Nb matches
        team.nb_matches += 1
        team_elo_history_entry = TeamEloRatingHistory(
            date=match_date,
            team_id=team.id,
            team_name=team.name,
            elo_rating=updated_elo_rating,
            elo_rating_gain=elo_rating_gain,
            match_id=match.id,
            match_name=match.name,
            league_id=match.league.id,
            league_name=match.league_name,
        )
        team_elo_history_entries.append(team_elo_history_entry)
        logger_debug.debug(f"created elo_history_entry for '{team.name}'")
    # Update Team nb victory/defeats
    winner_team.nb_victories += 1
    loser_team.nb_defeats += 1

    # Update db
    logger_debug.debug("committing to db")
    commit_to_db(
        *winners,
        *losers,
        winner_team,
        loser_team,
        *elo_history_entries,
        *team_elo_history_entries,
        match,
        session=session,
    )
    logger.notif(f"updated players results for match id={match.id}")

    return dict_elo_rating_gains, dict_updated_elo_ratings


def update_players_rank(
    league_name: str, league_id: UUID, session: Session = None
) -> None:
    """Calc ranks and updated database
    Notes
    -----
    If wants to process in thread: session must be None (default).
    It will create it, this allows running it in its own thread.
    """
    # Get all players, sorted by top Elo to bottom Elo (descending order)
    logger = LOGGER
    logger_debug = logger.getChild("update_players_rank")

    if session is None:
        session = DB.get_session()
        is_session_provided = False
    else:
        is_session_provided = True

    try:
        # Fetch players
        logger_debug.debug("starting rank update, fetching sorted_players")
        sorted_players = player_manager.get_all_players_from_league(
            session=session,
            league_name=league_name,
            order_by=Player.elo_rating,
            order_descending=True,
        )
        # Update players
        playerleague_links = []
        rank_history_entries = []
        for new_rank, player in enumerate(sorted_players, start=1):
            # Fetch and update LinkPlayerLeague
            logger_debug.debug(f"reading link for {player.name=}")
            link = read_from_db(
                LinkPlayerLeague,
                where=(
                    LinkPlayerLeague.player_id == player.id,
                    LinkPlayerLeague.league_id == league_id,
                ),
                session=session,
                unique=True,
            )
            link.rank = new_rank
            current_best_rank = link.best_rank
            if (player.nb_matches > 3) and (
                (current_best_rank is None) or (current_best_rank > new_rank)
            ):
                link.best_rank = new_rank
            playerleague_links.append(link)

            # Update RankHistory with League
            rank_history_entry = RankHistory(
                player_id=player.id,
                player_name=player.name,
                league_id=league_id,
                league_name=league_name,
                rank=new_rank,
            )
            rank_history_entries.append(rank_history_entry)
            logger_debug.debug(f"created rank_history_entry for {player.name=}")
        # Commit
        commit_to_db(*playerleague_links, *rank_history_entries, session=session)
        logger.notif(f"updated players ranking in league={league_name}")
    finally:
        if not is_session_provided:
            session.close()


def apply_season_reset_to_all_players(
    session: Session,
    season_name: str,
    event_date: datetime = None,
    event_description: str = "",
) -> None:
    """
    Notes
    -----
    Must perform this on ALL players at same time, to avoid issues with players belonging
    to several leagues
    """
    logger = LOGGER.getChild("season_reset")
    logger.info("initiating Elo season reset")

    # Manage optional date
    if not event_date:
        event_date = now()

    list_objects_to_commit = []
    # Fetch all players
    list_players = player_manager.get_all_players(session=session)
    for player in list_players:
        ## Calc gain
        elo_rating_gain = calc_season_reset_elo_rating_gain(player.elo_rating)
        updated_elo_rating = player.elo_rating + elo_rating_gain
        ## Update player elo
        player.elo_rating = updated_elo_rating
        list_objects_to_commit.append(player)
        ## Create EloRatingHistory
        elo_rating_history = EloRatingHistory(
            date=event_date,
            player_id=player.id,
            player_name=player.name,
            elo_rating=updated_elo_rating,
            elo_rating_gain=elo_rating_gain,
            match_id=None,  # match.id,
            match_name=f"{season_name} reset",
            league_id=None,  # match.league.id,
            league_name=None,  # match.league_name,
        )
        list_objects_to_commit.append(elo_rating_history)
    # Commit
    commit_to_db(*list_objects_to_commit, session=session)

    # Declare this as an event
    event_manager.create_event(
        session=session,
        name=season_name,
        date=event_date,
        category=EventCategory.SEASON_RESET,
        description=event_description,
    )
    logger.notif(
        f"successfully performed season reset of {season_name=} ({event_description=})"
    )


def get_all_elo_rating_histories(
    session: Session,
    as_df: bool = False,
    limit_last: int = None,
) -> list[EloRatingHistory] | pd.DataFrame:
    return read_from_db(
        EloRatingHistory,
        session=session,
        order_by=EloRatingHistory.date,
        as_df=as_df,
        limit_last=limit_last,
    )


def get_all_elo_rating_histories_from_league(
    session: Session,
    league_name: str,
    as_df: bool = False,
    limit_last: int = None,
) -> list[EloRatingHistory] | pd.DataFrame:
    """
    Only records from matches inside the league only.
    Excludes matches from players who played elsewhere than this league

    Notes
    -----
    Might have a weird behaviour on graphs if a player gained Elo in another league and comes back to this league ?
    In this case, use `get_all_elo_rating_histories_from_players_in_league`
    """
    return read_from_db(
        EloRatingHistory,
        where=EloRatingHistory.league_name == league_name,
        session=session,
        order_by=EloRatingHistory.date,
        as_df=as_df,
        limit_last=limit_last,
    )


def get_all_elo_rating_histories_from_players_in_league(
    session: Session,
    league_name: str,
    as_df: bool = False,
    limit_last: int = None,
):
    """
    All match records from players registered in the league.
    Also includes matches from players resgistered in several leagues.
    """
    # Fetch player_ids in league_name
    league_players = player_manager.get_all_players_from_league(
        session=session, league_name=league_name, as_df=False
    )
    player_ids = [player.id for player in league_players]
    return read_from_db(
        EloRatingHistory,
        where=EloRatingHistory.player_id.in_(player_ids),
        session=session,
        order_by=EloRatingHistory.date,
        as_df=as_df,
        limit_last=limit_last,
    )


def get_player_elo_rating_histories(
    session: Session,
    player_name: str,
    as_df: bool = False,
    limit_last: int = None,
) -> list[EloRatingHistory] | pd.DataFrame:
    return read_from_db(
        EloRatingHistory,
        where=EloRatingHistory.player_name == player_name,
        session=session,
        order_by=EloRatingHistory.date,
        as_df=as_df,
        limit_last=limit_last,
    )


def get_player_elo_rating_histories_in_league(
    session: Session,
    player_name: str,
    league_name: str,
    as_df: bool = False,
    limit_last: int = None,
) -> list[EloRatingHistory] | pd.DataFrame:
    return read_from_db(
        EloRatingHistory,
        where=(
            EloRatingHistory.player_name == player_name,
            EloRatingHistory.league_name == league_name,
        ),
        session=session,
        order_by=EloRatingHistory.date,
        as_df=as_df,
        limit_last=limit_last,
    )


def get_team_elo_rating_histories(
    session: Session,
    team_name: str,
    as_df: bool = False,
    limit_last: int = None,
) -> list[EloRatingHistory] | pd.DataFrame:
    return read_from_db(
        TeamEloRatingHistory,
        where=TeamEloRatingHistory.team_name == team_name,
        session=session,
        order_by=TeamEloRatingHistory.date,
        as_df=as_df,
        limit_last=limit_last,
    )
