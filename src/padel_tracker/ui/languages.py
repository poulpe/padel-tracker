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
    "best_elo_rating": "Meilleur Elo",
    "nb_matches": "Matches",
    "nb_victories": "V",
    "nb_defeats": "D",
    "player_name": "Joueur",
    "team_name": "Équipe",
    "last_match_date": "Dernier match",
    "score": "Score",
    "match_name": "Match",
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
    "empty_database_error": "Il n'y a aucun match pour le moment. Assure toi de rentrer tes premiers joueurs via la page 'Nouveau joueur', puis ton premier match via la page 'Nouveau match'.",
    "not_enough_players_database_error": "Il n'y a pas encore assez de joueurs enregistrés pour faire un match. Assure toi d'avoir créé au moins 4 joueurs via la page 'Nouveau joueur'.",
    "check_logs": "Consulter les logs",
    "delete_player": "Supprimer un joueur",
    "delete_match": "Supprimer un match",
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
    # UI message
    "language": "Language",
    "add_match": "Add match",
    "add_player": "Add player",
    "check_player": "Check player",
    "check_team": "Check team",
    "match_history": "Match history",
    "last_match_history": "Last matches history",
    "billboard": "Billboard",
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
    "empty_database_error": "There's no match at the moment. Ensure your players are declared via the page 'New player' and enter your first match via the page 'New match'.",
    "not_enough_players_database_error": "Not enough players yet registered to make a match. Ensure you've created at least 4 players via the page 'New player'.",
    "check_logs": "Check logs",
    "delete_player": "Delete player",
    "delete_match": "Delete match",
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
