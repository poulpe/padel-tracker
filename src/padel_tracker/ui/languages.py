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
    "add_match": "Créer match",
    "match_history": "Historique des matches",
    "billboard": "Billboard",
    "matches": "Matchs",
    "analytics": "Analytics",
    "submit": "Roule ma poule",
    "ranking": "Classement",
    "players_teams": "Joueurs/Equipes",
    "players_table": "Tableau des joueurs",
    "team1": "Equipe 1",
    "team2": "Equipe 2",
    "player1": "Joueur 1",
    "player2": "Joueur 2",
    "time": "Heure",
    "match_added_success": "Match enregistré !",
    "match_added_error": "Impossible d'ajouter le match, erreur inconnue",
    "match_exists_error": "Le match a déja été enregistré",
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
    "match_history": "Match history",
    "billboard": "Billboard",
    "matches": "Matches",
    "analytics": "Analytics",
    "submit": "Submit",
    "ranking": "Ranking",
    "players_teams": "Players/Teams",
    "players_table": "Players table",
    "team1": "Team 1",
    "team2": "Team 2",
    "player1": "Player 1",
    "player2": "Player 2",
    "time": "Time",
    "match_added_success": "Match added with success !",
    "match_added_error": "Unknown error during match creation",
    "match_exists_error": "Match already added",
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
