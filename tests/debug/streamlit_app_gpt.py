import streamlit as st
import pandas as pd

from padel_tracker.database.db import get_db_session
from padel_tracker.services.player_manager import (
    create_player,
    get_player_from_name,
    get_all_players,
    create_team,
    get_team_from_players_name,
)
from padel_tracker.services.match_manager import create_match, process_finished_match
from padel_tracker.utils.datetime_utils import now

# 1. Configuration de l'application
st.set_page_config(page_title="Padel Tracker", layout="wide")

# 2. Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Menu", ["Classement", "Joueur", "Saisie de Matchs", "Administration"]
)

# print("coucou")

# 3. Classement des joueurs
if menu == "Classement":
    st.title("Classement des Joueurs")
    with get_db_session() as session:
        players = get_all_players(session=session)
        # Créer un tableau des joueurs
        list_data = [
            {
                "Nom": p.name,
                "Elo": p.elo_rating,
                "Rang": p.rank,
                "Matches": p.nb_matches,
                "V": p.nb_victories,
                "D": p.nb_defeats,
            }
            for p in players
        ]
        df = pd.DataFrame(list_data)
        st.dataframe(df, hide_index=True)

# 4. Détail d'un joueur
elif menu == "Joueur":
    st.title("Détail d'un Joueur")
    with get_db_session() as session:
        players = get_all_players(session=session)
        player_names = {p.name: p.id for p in players}

        selected_player = st.selectbox(
            "Choisissez un joueur", list(player_names.keys())
        )
        player_id = player_names[selected_player]

        # Récupérer l'historique des rangs
        # rank_history = get_rank_history(session, player_id)
        #
        # if rank_history:
        #     df = pd.DataFrame([{"Date": rh.date, "Classement": rh.rank} for rh in rank_history])
        #     st.line_chart(df.set_index("Date")["Classement"])
        # else:
        #     st.warning("Aucun historique trouvé pour ce joueur.")

# 5. Saisie des matchs
elif menu == "Saisie de Matchs":
    st.title("Saisie de Résultats de Matchs")

    with get_db_session() as session:
        players = get_all_players(session=session)
        player_names = [p.name for p in players]

        col1, col2 = st.columns(2)
        with col1:
            team1 = st.multiselect("Équipe 1", player_names, max_selections=2)
        with col2:
            team2 = st.multiselect("Équipe 2", player_names, max_selections=2)

        score = st.text_input("Entrez le score (ex : 6-4, 7-5)")

        if st.button("Enregistrer le match"):
            if len(team1) == 2 and len(team2) == 2:
                create_match(
                    session=session, teams=[team1, team2], score=score, date=now()
                )  # Add players=
                st.success("Match enregistré avec succès.")
            else:
                st.error("Veuillez sélectionner deux joueurs par équipe.")

# 6. Administration
elif menu == "Administration":
    st.title("Administration")

    with get_db_session() as session:
        new_player_name = st.text_input("Nom du joueur")
        if st.button("Ajouter un joueur"):
            create_player(session=session, name=new_player_name)
            st.success(f"Joueur {new_player_name} ajouté avec succès.")
