import streamlit as st

from padel_tracker.database.db import DB
from padel_tracker.services.match_manager import get_all_matches, get_last_matches
from padel_tracker.models.matches import MatchScore


def define_cards_css() -> None:
    # Define CSS
    st.markdown(
        """
        <style>
            .match-card {
                border: 2px solid #e6e6e6;
                border-radius: 10px;
                padding: 15px;
                /*width: 400px;
                background-color: #f9f9f9;*/
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
                /*font-family: Arial, sans-serif;*/
            }
            .match-card-team {
                display: flex;
                justify-content: space-between;
                font-size: 16px;
                font-weight: bold;
                /*color: #666;*/ 
            }
            .match-card-score-box {
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-left: 5px;
            }
            .match-card-winner-icon {
                width: 16px;
                height: 16px;
                margin-right: 7px;
                display: flex;
                /*align-items: center;*/
                justify-content: center;
            }
            .match-card-date {
                margin-top: 10px;
                text-align: center;
                font-size: 14px;
                color: #666;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_match_card(
    team1: str,
    team2: str,
    team1_won: bool = None,
    date: str = None,
    games_set1_team1: int = None,
    games_set1_team2: int = None,
    games_set2_team1: int = None,
    games_set2_team2: int = None,
    games_set3_team1: int = None,
    games_set3_team2: int = None,
) -> None:
    # Sets winner logic for icon (no icon if no team won)
    if team1_won is None:
        team2_won = None
    else:
        team2_won = not team1_won

    def render_score_box(score: str | int) -> str:
        """Render a framed box for a score (empty if None)"""
        return f'<div class="match-card-score-box">{score if score is not None else " "}</div>'

    def render_team(team_name: str, is_winner: bool) -> str:
        """Render aligned container with or without winner icon"""
        icon = ""
        if is_winner:
            icon = "✌️"
        # Strip team length if too long (only on mobile)
        try:
            device_type = st.session_state.device_type
        except Exception:
            device_type = "pc"
        if device_type == "mobile":
            max_team_length = 15
            max_player_length = int(max_team_length / 2)
            if len(team_name) > max_team_length:
                player1, player2 = team_name.split("/")
                if len(player1) > max_player_length + 1:
                    player1 = player1[:max_player_length]
                    player1 += "."
                if len(player2) > max_player_length + 1:
                    player2 = player2[:max_player_length]
                    player2 += "."
                team_name = f"{player1}/{player2}"
        return f"""
            <div class="match-card-team">
                <div class="match-card-winner-icon">{icon}</div>
                <div>{team_name}</div>
            </div>
        """

    def render_date(date) -> str:
        if date is not None:
            return f"{date}"
        else:
            return " "

    st.markdown(
        f"""
        <div class="match-card">
            <div class="match-card-team">
                <div>{render_team(team1, team1_won)}</div>
                <div style="display: flex;">
                    {render_score_box(games_set1_team1)}
                    {render_score_box(games_set2_team1)}
                    {render_score_box(games_set3_team1)}
                </div>
            </div>
            <div class="match-card-team">
                <div>{render_team(team2, team2_won)}</div>
                <div style="display: flex;">
                    {render_score_box(games_set1_team2)}
                    {render_score_box(games_set2_team2)}
                    {render_score_box(games_set3_team2)}
                </div>
            </div>
            <div class="match-card-date">{render_date(date)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


def make_match_cards(limit_last: int | None = 10) -> None:
    with DB.get_session() as session:
        if not limit_last:
            list_matches = get_all_matches(session=session)
        else:
            list_matches = get_last_matches(session=session, limit_last=limit_last)
        list_matches.reverse()  # From latest to oldest
        for match in list_matches:
            match_score = MatchScore.from_string(match.score)
            display_match_card(
                team1=str(match.teams[0]),
                team2=str(match.teams[1]),
                team1_won=match.team1_won,
                date=match.date.strftime("%d %b %Y %H:%M"),
                games_set1_team1=match_score.games_set1_team1,
                games_set1_team2=match_score.games_set1_team2,
                games_set2_team1=match_score.games_set2_team1,
                games_set2_team2=match_score.games_set2_team2,
                games_set3_team1=match_score.games_set3_team1,
                games_set3_team2=match_score.games_set3_team2,
            )


# TODO : display player_card
def display_player_card():
    return NotImplementedError
