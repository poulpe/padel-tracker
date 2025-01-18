import streamlit as st

def display_match_card(
    date:str,
    team1:str,
    team2:str,
    team1_won:bool,
    games_set1_team1:int,
    games_set1_team2:int,
    games_set2_team1:int=None,
    games_set2_team2:int=None,
    games_set3_team1:int=None,
    games_set3_team2:int=None,
) -> None:
    # Define CSS
    st.markdown("""
        <style>
            .match-card {
                border: 2px solid #e6e6e6;
                border-radius: 10px;
                padding: 15px;
                width: 400px;
                background-color: #f9f9f9;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
                font-family: Arial, sans-serif;
            }
            .match-card-team {
                display: flex;
                justify-content: space-between;
                font-size: 18px;
                font-weight: bold;
            }
            .match-card-score {
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
                font-size: 20px;
            }
            .match-card-score-box {
                width: 35px;
                height: 35px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-left: 5px;
            }
            .match-card-winner-icon {
                margin-left: 10px;
                font-size: 18px;
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

    def render_score_box(score):
        """Affiche une case encadrée pour un score (vide si None)."""
        return f'<div class="match-card-score-box">{score if score is not None else ""}</div>'

    winner_icon = "<span class='match-card-winner-icon'>✌️</span>"
    winner_icon_team1 = winner_icon if team1_won else ""
    winner_icon_team2 = winner_icon if not team1_won else ""

    st.markdown(f"""
        <div class="match-card">
            <div class="match-card-team">
                <div>{team1} {winner_icon_team1}</div>
                <div style="display: flex;">
                    {render_score_box(games_set1_team1)}
                    {render_score_box(games_set2_team1)}
                    {render_score_box(games_set3_team1)}
                </div>
            </div>
            <div class="match-card-team">
                <div>{team2} {winner_icon_team2}</div>
                <div style="display: flex;">
                    {render_score_box(games_set1_team2)}
                    {render_score_box(games_set2_team2)}
                    {render_score_box(games_set3_team2)}
                </div>
            </div>
            <div class="match-card-date">Date : {date}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
