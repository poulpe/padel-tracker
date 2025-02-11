from enum import StrEnum
from dataclasses import dataclass

import streamlit as st

from padel_tracker.utils.logs import get_logger

_DICT_TO_FR = {
    # Models fields
    "name": "Nom",
    "date": "Date",
    "elo_rating": "Points Elo",
    "elo_rating_gain": "Gain de points",
    "rank": "Rang",
    "best_rank": "Meilleur rang",
    "best_elo_rating": "Meilleur Elo",
    "nb_matches": "Matches",
    "nb_victories": "V",
    "nb_defeats": "D",
    "player_name": "Joueur",
    "team_name": "Équipe",
    "last_match_date": "Dernier match",
    "score": "Score",
    "match_name": "Match",
    "league": "Ligue",
    "leagues": "Ligues",
    "league_name": "Ligue",
    "league_names": "Ligues",
    "user": "Utilisateur",
    # UI message
    "language": "Langue",
    "add_match": "Nouveau match",
    "add_player": "Nouveau joueur",
    "check_player": "Fiche de joueur",
    "check_team": "Fiche d'équipe",
    "match_history": "Historique des matches",
    "last_match_history": "Historique des derniers matchs",
    "billboard": "Billboard",
    "overview": "Vue générale",
    "matches": "Matchs",
    "analytics": "Analytics",
    "administration": "Administration",
    "submit": "Roule ma poule",
    "ranking": "Classement",
    "players_teams": "Joueurs/Équipes",
    "players_table": "Tableau des joueurs",
    "team": "Équipe",
    "team1": "Équipe 1",
    "team2": "Équipe 2",
    "player": "Joueur",
    "player1": "Joueur 1",
    "player2": "Joueur 2",
    "time": "Heure",
    "match_added_success": " Match enregistré !",
    "match_added_error": " Impossible d'ajouter le match, erreur inconnue",
    "match_exists_error": " Le match a déja été enregistré",
    "match_not_finished_error": "Les calculs sont pas bons Kévin, le score ne colle pas",
    "see_updated_elo_below": "Voici les nouveaux points Elo:",
    "player_added_success": " a été ajouté avec succès !",
    "player_added_error": " Impossible d'ajouter le joueur, erreur inconnue:",
    "player_exists_error": " a déja été enregistré",
    "player_invalid_name_error": " n'est pas un nom valide. Assure toi qu'il contient au moins 2 caractères, pas de chiffres et qu'il représente un vrai nom de champion !",
    "player_not_selected_error": " Assure toi d'avoir selectionné tous les joueurs",
    "player_deletion_error": "Erreur pendant la suppression du joueur: ",
    "team_same_player_error": " Le meme joueur a été sélectionné dans une meme équipe, 1v2 c'est pas fairplay !",
    "team_not_found_error": " Cette équipe n'a jamais joué un match ensemble. C'est peut-etre dommage, mais en tout cas y'a rien à afficher",
    "same_player_in_both_teams_error": " Un joueur est présent dans les 2 équipes en meme temps, c'est chaud de se dupliquer des 2 cotés du terrain !",
    "next_feature": "BIENTOT",
    "ranking_evolution": "Évolution du classement",
    "ranking_evolution_over_x_last_matches": "Évolution du classement sur les {x} derniers matchs",
    "result": "Résultat",
    "victory": "Victoire",
    "defeat": "Défaite",
    "ratio_vd": "V/D",
    "nb_won_games_diff": "Différence de jeux gagnés",
    "metric": "Métrique",
    "evolution": "Évolution",
    "creation_date": "Date d'ajout",
    "player_relationships": "Esprit d'équipe",
    "best_teammate": "Meilleur partenaire",
    "x_victories_together": "{x} victoires ensemble",
    "most_teammate": "Partenaire de coeur",
    "x_matches_together": "{x} matchs ensemble",
    "black_beast": "Bête noire",
    "x_defeats_against": "{x} défaites contre lui/elle",
    "black_beasts": "Bêtes noires",
    "x_defeats_against_them": "{x} défaites contre eux/elles",
    "favorite_victim": "Victime préférée",
    "x_victories_against": "{x} victoires contre lui/elle",
    "favorite_victims": "Victimes préférées",
    "x_victories_against_them": "{x} victoires contre eux/elles",
    "no_league_database_error": "Il n'y a aucune ligue à afficher pour le moment. Enregistre une ligue via la page 'Nouvelle ligue'",
    "no_match_database_error": "Il n'y a aucun match dans cette ligue pour le moment. Assure toi de rentrer tes premiers joueurs via la page 'Nouveau joueur', puis ton premier match via la page 'Nouveau match'.",
    "not_enough_players_database_error": "Il n'y a pas encore assez de joueurs enregistrés dans cette ligue pour faire un match. Assure toi d'avoir créé au moins 4 joueurs via la page 'Nouveau joueur'.",
    "check_logs": "Consulter les logs",
    "delete_player": "Supprimer un joueur",
    "delete_match": "Supprimer un match",
    "delete": "Supprime",
    "player_deleted": " a été supprimé. Bye bye 😢",
    "player_already_deleted": " a déja été supprimé, arrête de t'acharner, c'était suffisant douloureux comme ça 😭",
    "all_players_not_in_league_error": "Il y a des joueurs qui ne font pas parties de la ligue, assure toi que tous tes champions font bien partie de la meme ligue pour enregistrer un match ensemble.",
    "add_league": "Nouvelle ligue",
    "league_added_success": " a été ajouté avec succès !",
    "league_exists_error": " a déja été enregistré",
    "league_invalid_name_error": " n'est pas un nom de ligue valide. Assure toi qu'il contient au moins 2 caractères, pas de chiffres et qu'il représente un vrai nom de ligue de batard !",
    "league_added_error": " Impossible d'ajouter la ligue, erreur inconnue:",
    "assign_league": "Recrute dans une ligue",
    "player_already_in_league_error": "  a déja été enregistré dans la ligue ",
    "assigned_league_to_player_success": " a bien été enregistré dans la ligue ",
    "time_scale": "Échelle temps",
    "time_scale_help_message": "Montre le temps réel entre les matchs sur le graph",
    "welcome_not_logged": "Bienvenue sur Padel Tracker !",
    "padel_tracker_kezako": """
        **Padel Tracker** est une petite appli qui te permet de garder une trace de tes matchs de Padel et de suivre ton évolution et celle de tes potes au cours du temps.    

        L'appli intègre un systeme de classement type Elo, pratique pour etre utilisée au sein d'un groupe de joueurs réguliers (*Ligue*).  
        Elle permet aussi d'analyser tes performances croisées avec les différents équipiers de ta ligue, utile pour consulter les relations et identifier les paires qui fonctionnent bien (ou moins bien... 😬)

        - Alors, qui sera le gros Bill de ta ligue ? 
        - Qui s'avérera être le/la partenaire de choix avec qui tu défonces tout ?
        - Qui sera la lanterne rouge et ne manquera pas de payer son coup au prochain match ?

        Pour te connecter, plusieurs options:
        - Crée un compte / connecte toi via un standard email/mot de passe.  
          (_l'appli utilise [`Auth0`](http://www.auth0.com) pour l'authentification, si tu reçois des mails sous ce nom là, c'est OK_)    
        - Tu peux aussi utiliser un compte `Google` pour te connecter rapidement  
            _(l'appli ne fait rien de tes infos persos, au delà de garder en mémoire un identifiant unique te permettant de t'identifer la prochaine fois)_

        Projet Open-Source, plus d'infos sur le [repo Github du projet](https://github.com/poulpe/padel-tracker)
    """,
    "click_to_login": "Clique ci dessous pour t'identifier ou t'inscrire",
    "login_signup": "Se connecter / S'inscrire",
    "login": "Se connecter",
    "click_to_connect_as_guest": "Si t'es timide, tu peux juste venir y jeter un oeil comme ça",
    "connect_as_guest": "Se connecter en tant qu'invité",
    "my_account": "Mon compte",
    "manage_account": "Gérer mon compte",
    "logout": "Se déconnecter",
    "finalize_signup": "Bienvenue Champion, finalise ton inscription !",
    "existing_league": "Ligue",
    "existing_league_message": "Ta ligue existe déja et tu souhaites la rejoindre ? Laisse vide sinon",
    "finalize_signup_existing_player_message_header": "Peut-être que tu as déja été ajouté en tant que joueur ?",
    "finalize_signup_existing_player_message_sub": "Si tu te reconnais, tu peux t'assigner:",
    "finalize_signup_not_existing_player_message_header": "Tu ne t'es pas trouvé(e) au dessus ?",
    "finalize_signup_not_existing_player_message_sub": "C'est ici que ça se passe alors:",
    "existing_player": "En fait, c'est moi:",
    "username_help": "Faut que ce soit un putain de nom de Champion ! Idéalement à consonnance espagnole donc... Juste pas de caractères spéciaux, ni de chiffres",
    "user_added_success": "Nickel, ton compte est en cours de création !",
    "existing_league_help": "Ta ligue existe déja et tu souhaites la rejoindre ? Laisse vide sinon. Tu pourras toujours créer/rejoindre une ligue plus tard dans le menu",
}

_DICT_TO_EN = {
    # Models fields
    "name": "Name",
    "date": "Date",
    "elo_rating": "Elo rating",
    "elo_rating_gain": "Elo rating gain",
    "rank": "Rank",
    "best_rank": "Best rank",
    "best_elo_rating": "Best Elo rating",
    "nb_matches": "Matches",
    "nb_victories": "V",
    "nb_defeats": "D",
    "player_name": "Player",
    "team_name": "Team",
    "last_match_date": "Last match",
    "score": "Score",
    "match_name": "Match",
    "league": "League",
    "leagues": "Leagues",
    "league_name": "League",
    "league_names": "Leagues",
    # UI message
    "language": "Language",
    "add_match": "Add match",
    "add_player": "Add player",
    "check_player": "Check player",
    "check_team": "Check team",
    "match_history": "Match history",
    "last_match_history": "Last matches history",
    "billboard": "Billboard",
    "overview": "Overview",
    "matches": "Matches",
    "analytics": "Analytics",
    "administration": "Administration",
    "submit": "Submit",
    "ranking": "Ranking",
    "players_teams": "Players/Teams",
    "players_table": "Players table",
    "team": "Team",
    "team1": "Team 1",
    "team2": "Team 2",
    "player": "Player",
    "player1": "Player 1",
    "player2": "Player 2",
    "time": "Time",
    "match_added_success": " Match added successfully !",
    "match_added_error": " Unknown error during match creation",
    "match_exists_error": " Match already added",
    "match_not_finished_error": "Scores are not valid for a finished match, please double check",
    "see_updated_elo_below": "See updated elo ratings below:",
    "player_added_success": " added successfully !",
    "player_added_error": " Unknown error during player creation:",
    "player_exists_error": " has already been added",
    "player_invalid_name_error": " is not a valid name. Make sure it has at least 2 alphabetical characters, no number and that it represents a valid champion name !",
    "player_not_selected_error": "Make sure all players have been selected",
    "player_deletion_error": "Unexpected error during player deletion: ",
    "team_same_player_error": " Same player has been selected in one team, 1v2 is not fairplay !",
    "team_not_found_error": " This team has never played a match together. Maybe a pity... but anyway, there's nothing to display !",
    "same_player_in_both_teams_error": " A player is in both teams, it's hard to be in 2 places at the same time",
    "next_feature": "SOON",
    "ranking_evolution": "Ranking evolution",
    "ranking_evolution_over_x_last_matches": "Ranking evolution over the {x} last matches",
    "result": "Result",
    "victory": "Victory",
    "defeat": "Defeat",
    "ratio_vd": "V/D",
    "nb_won_games_diff": "Won games difference",
    "metric": "Metric",
    "evolution": "Evolution",
    "creation_date": "Creation date",
    "player_relationships": "Team spirit",
    "best_teammate": "Best teammate",
    "x_victories_together": "{x} victories together",
    "most_teammate": "Most played teammate",
    "x_matches_together": "{x} matches together",
    "black_beast": "Black beast",
    "x_defeats_against": "{x} defeats against",
    "black_beasts": "Black beasts",
    "x_defeats_against_them": "{x} defeats against them",
    "favorite_victim": "Favorite victim",
    "x_victories_against": "{x} victories against",
    "favorite_victims": "Favorite victims",
    "x_victories_against_them": "{x} victories against them",
    "no_league_database_error": "No league for the moment. Register a first league via the page 'New league'",
    "no_match_database_error": "There's no match in this league at the moment. Ensure your players are declared via the page 'New player' and enter your first match via the page 'New match'.",
    "not_enough_players_database_error": "Not enough players yet registered in this league to make a match. Ensure you've created at least 4 players via the page 'New player'.",
    "check_logs": "Check logs",
    "delete_player": "Delete player",
    "delete_match": "Delete match",
    "delete": "Delete",
    "player_deleted": " has been deleted. Bye bye 😢",
    "player_already_deleted": " has already been deleted, please stop, it was already painful enough 😭",
    "add_league": "Add league",
    "all_players_not_in_league_error": "Some/all players are not part of the league, make sure they are part of the league so you can register a match together",
    "league_added_success": " added successfully !",
    "league_added_error": " Unknown error during league creation:",
    "league_exists_error": " has already been added",
    "league_invalid_name_error": " is not a valid league name. Make sure it has at least 2 alphabetical characters, no number and that it represents a valid champion's league name !",
    "assign_league": "Assign player to league",
    "player_already_in_league_error": "  has already been assigned to this league",
    "assigned_league_to_player_success": " has been successfully assigned in the league ",
    "time_scale": "Time scale",
    "time_scale_help_message": "Show real time difference between matches on the graph",
    "welcome_not_logged": "Welcome to Padel Tracker!",
    "padel_tracker_kezako": """
        **Padel Tracker** is a small app that lets you keep track of your Padel matches and monitor your progress, as well as that of your friends, over time.    

        The app includes an Elo-based ranking system, perfect for use within a group of regular players (*League*).  
        It also allows you to analyze your performance alongside different teammates in your league, helping you identify which pairs work well together (or... not so well 😬).

        - So, who will be the big shot of your league?  
        - Who will turn out to be your ultimate winning partner?  
        - Who will end up at the bottom and owe a round of drinks at the next match?  

        You have several options to log in:
        - Create an account / log in with a standard email/password.  
          (_The app uses [`Auth0`](http://www.auth0.com) for authentication. If you receive emails under this name, that's expected._)    
        - You can also log in quickly using a `Google` account  
            _(The app doesn’t use your personal data beyond storing a unique identifier to recognize you next time.)_

        Open-source project, more info on the [project's GitHub repository](https://github.com/poulpe/padel-tracker).
    """,
    "click_to_login": "Click below to log in or sign up",
    "login_signup": "Log in / Sign up",
    "login": "Log in",
    "click_to_connect_as_guest": "If you're feeling shy, you can just take a look around",
    "connect_as_guest": "Log in as a guest",
    "my_account": "My account",
    "manage_account": "Manage my account",
    "logout": "Log out",
    "finalize_signup": "Welcome Champion, finalize your registration !",
    "existing_league": "League",
    "existing_league_message": "Does your league already exist and you want to join? Leave blank otherwise.",
    "finalize_signup_existing_player_message_header": "Maybe you've already been added as a player ?",
    "finalize_signup_existing_player_message_sub": "If you recognize yourself, you can assign yourself:",
    "finalize_signup_not_existing_player_message_header": "Didn't find yourself above?",
    "finalize_signup_not_existing_player_message_sub": "Then this is the place for you:",
    "existing_player": "Actually, that's me:",
    "username_help": "It has to be a badass Champion name! Ideally, something Spanish-sounding… Just no special characters or numbers",
    "user_added_success": "Great! Your account is being created!",
    "existing_league_help": "Does your league already exist, and you want to join? Leave blank otherwise. You can always create/join a league later from the menu",
}


class Language(StrEnum):
    FR = "Français"
    EN = "English"


_DICT_LANGUAGES = {
    Language.FR: _DICT_TO_FR,
    Language.EN: _DICT_TO_EN,
}


@dataclass  # For hashable compatibility with streamlit st.cache_data
class LanguageTranslator:
    lang: str | Language

    def __post_init__(self):
        self.dict_lang = _DICT_LANGUAGES[self.lang]

    def __call__(self, key: str):
        try:
            result = self.dict_lang[key]
        except KeyError:
            result = key[0].upper() + key[1:].replace("_", " ") if key else key
            logger = get_logger("ui.language")
            logger.error(f"translation for '{key}' in lang={str(self.lang)} is missing")
        return result


def update_session_state_translator() -> None:
    st.session_state.translator = LanguageTranslator(st.session_state.language)


DEFAULT_LANGUAGE = Language.FR
DEFAULT_TRANSLATOR = LanguageTranslator(DEFAULT_LANGUAGE)

SUPPORTED_LANGUAGES = (Language.FR, Language.EN)
