# from padel_tracker.services.player_manager import (
#     get_player_from_name,
#     get_team_from_players_name,
# )
# from padel_tracker.services.match_manager import create_match, get_match_from_id
#
#
# def test_create_match(db_session):
#     # Retrieve players
#     match = create_match(db_session, team1_name="Team A", team2_name="Team B")
#     assert match.team1_name == "Team A"
#     assert match.team2_name == "Team B"
#     assert match.score is None
#
#
# def test_get_match_by_id(db_session):
#     match = create_match(db_session, team1_name="Team X", team2_name="Team Y")
#     retrieved_match = get_match_from_id(db_session, match.id)
#     assert retrieved_match is not None
#     assert retrieved_match.team1_name == "Team X"
#     assert retrieved_match.team2_name == "Team Y"
