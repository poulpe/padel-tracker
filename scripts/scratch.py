# from padel_tracker.utils.paths import get_absolute_path
# from padel_tracker.database.db import get_db_session
# from padel_tracker.services.ranking_manager import get_elo_rating_history
# from padel_tracker.services.player_manager import get_all_players
# from padel_tracker.services.match_manager import check_match_not_already_created

# with get_db_session() as session:
#     df_elo_history = get_elo_rating_history(session, as_df=True).copy()
#     df_elo_history.to_csv(
#         get_absolute_path(__file__, "../src/padel_tracker/ui/df_elo_history.csv"),
#         index=False,
#         mode="w"
#     )

# with get_db_session() as session:
#     df_players = get_all_players(session, as_df=True).copy()
#     df_players.head(5)
