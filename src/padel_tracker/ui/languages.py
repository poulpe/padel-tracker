from enum import StrEnum

from padel_tracker.utils.logs import get_logger

_DICT_TO_FR = {
    # Models fields
    "name": "Nom",
    "date": "Date",
    "elo_rating": "Points Elo",
    "elo_rating_gain": "Gain de points",
    "rank": "Rang",
    "best_rank": "Meilleur rang",
    "nb_matches": "Matches",
    "nb_victories": "V",
    "nb_defeats": "D",
    "player_name": "Joueur",
    "team_name": "Équipe",
    "last_match_date": "Dernier match",
    "score": "Score",
    # UI message
    "language": "Langue",
    "add_match": "Nouveau match",
    "add_player": "Nouveau joueur",
    "match_history": "Historique des matches",
    "last_match_history": "Historique des derniers matchs",
    "billboard": "Billboard",
    "matches": "Matchs",
    "analytics": "Analytics",
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
    "player_added_success": " a été ajouté avec succès !",
    "player_added_error": " Impossible d'ajouter le joueur, erreur inconnue:",
    "player_exists_error": " a déja été enregistré",
    "player_not_selected_error": " Assure toi d'avoir selectionné tous les joueurs",
    "team_same_player_error": " Le meme joueur a été sélectionné dans une meme équipe, 1v2 c'est pas fairplay !",
    "same_player_in_both_teams_error": " Un joueur est présent dans les 2 équipes en meme temps, c'est chaud de se dupliquer des 2 cotés du terrain !",
    "next_feature": "BIENTOT",
}

_DICT_TO_EN = {
    # Models fields
    "name": "Name",
    "date": "Date",
    "elo_rating": "Elo rating",
    "elo_rating_gain": "Elo rating gain",
    "rank": "Rank",
    "best_rank": "Best rank",
    "nb_matches": "Matches",
    "nb_victories": "V",
    "nb_defeats": "D",
    "player_name": "Player",
    "team_name": "Team",
    "last_match_date": "Last match",
    "score": "Score",
    # UI message
    "language": "Language",
    "add_match": "Add match",
    "add_player": "Add player",
    "match_history": "Match history",
    "last_match_history": "Last matches history",
    "billboard": "Billboard",
    "matches": "Matches",
    "analytics": "Analytics",
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
    "player_added_success": " added successfully !",
    "player_added_error": " Unknown error during player creation:",
    "player_exists_error": " has already been added",
    "player_not_selected_error": "Make sure all players have been selected",
    "team_same_player_error": " Same player has been selected in one team, 1v2 is not fairplay !",
    "same_player_in_both_teams_error": " A player is in both teams, it's hard to be in 2 places at the same time",
    "next_feature": "SOON",
}


class Language(StrEnum):
    FR = "Français"
    EN = "English"


_DICT_LANGUAGES = {
    Language.FR: _DICT_TO_FR,
    Language.EN: _DICT_TO_EN,
}


class LanguageTranslator:
    def __init__(self, lang: str | Language):
        self.lang = lang
        self.dict_lang = _DICT_LANGUAGES[lang]

    def __call__(self, key: str):
        try:
            result = _DICT_LANGUAGES[self.lang][key]
        except KeyError:
            result = key
            logger = get_logger("ui.language")
            logger.error(f"translation for '{key}' in lang={str(self.lang)} is missing")
        return result


DEFAULT_LANGUAGE = Language.FR
DEFAULT_TRANSLATOR = LanguageTranslator(DEFAULT_LANGUAGE)

SUPPORTED_LANGUAGES = (Language.FR, Language.EN)
