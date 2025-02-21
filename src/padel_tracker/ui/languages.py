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
    "nb_players": "Nombre de joueurs",
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

        L'appli intègre un système de classement type Elo, pratique pour être utilisée au sein d'un groupe de joueurs réguliers (*Ligue*).            
        Elle permet aussi d'analyser tes performances croisées avec les différents équipiers de ta ligue, utile pour identifier les paires qui fonctionnent bien (ou moins bien... 😬)     

        - Alors, qui sera le gros Bill de ta ligue ? 
        - Qui s'avérera être le/la partenaire de choix avec qui tu défonces tout ?
        - Qui sera la lanterne rouge et ne manquera pas de payer son coup au prochain match ?

        **Note**: le système de classement bonifie l'écart de jeux gagnés entre les 2 équipes dans un match.   
        Donc, même menés à 5-0, ne baissez pas les bras : chaque point compte !   

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
    "finalize_signup": "Bienvenue Champion(ne), finalise ton inscription !",
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
    "join_league": "Rejoindre une ligue",
    "feedback_header": "Formulaire de feedback",
    "feedback_button": "Un bug ? Une demande ?",
    "feedback_subheader_line1": "Un bug ?",
    "feedback_subheader_line2": "Une amélioration que tu aimerais ou une demande particulière ?",
    "feedback_subsubheader": """
        N'hesite pas à me faire ton retour !     
        _(Meme si c'est juste pour râler à cause de ces 'scrogneugneus' de bugs ou juste de me remercier parce que tu trouves l'appli cool !)_
    """,
    "feedback_title": "Titre",
    "feedback_description": "Description",
    "feedback_submit_success": """
        Message envoyé avec succès, merci de ton retour ! 
        Si tu veux consulter le suivi du problème: """,
    "feedback_submit_error": "Problème durant l'envoi du feedback, cette appli est definitivement buggée du cul...",
    "private_league": "Ligue privée",
    "private_league_help": "Faire en sorte que la ligue ne soit visible que pour toi et pour les joueurs que tu ajouteras manuellement via le menu 'Gérer la ligue'",
    "public_league": "Ligue publique",
    "my_league": "Ma ligue",
    "manage_league": "Gérer la ligue",
    "description": "Description",
    "no_description_yet": "Pas de description pour le moment...",
    "add_in_league": "Recrute dans la ligue",
    "remove_from_league": "Retire un joueur de la ligue",
    "league_admins": "Administrateurs de la ligue",
    "league_administration": "Gestion de la ligue",
    "player_removed": " a été retiré. Bye bye 😢",
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
    "join_league": "Join a league",
    "feedback_header": "Feedback Form",
    "feedback_button": "A bug? A request?",
    "feedback_subheader_line1": "A bug?",
    "feedback_subheader_line2": "An improvement you'd like or a specific request?",
    "feedback_subsubheader": """
        Feel free to share your feedback!     
        _(Even if it's just to rant about those damn bugs or to thank me because you find the app cool!)_
    """,
    "feedback_title": "Title",
    "feedback_description": "Description",
    "feedback_submit_success": """
        Message sent successfully, thanks for your feedback!  
        If you want to track the issue: """,
    "feedback_submit_error": "Error while sending feedback, this app is definitely buggy as hell...",
}

_DICT_TO_ES = {
    # Models fields
    "name": "Nombre",
    "date": "Fecha",
    "elo_rating": "Puntos Elo",
    "elo_rating_gain": "Ganancia de puntos",
    "rank": "Rango",
    "best_rank": "Mejor rango",
    "best_elo_rating": "Mejor Elo",
    "nb_matches": "Partidos",
    "nb_victories": "V",
    "nb_defeats": "D",
    "player_name": "Jugador",
    "team_name": "Equipo",
    "last_match_date": "Último partido",
    "score": "Puntuación",
    "match_name": "Partido",
    "league": "Liga",
    "leagues": "Ligas",
    "league_name": "Liga",
    "league_names": "Ligas",
    "user": "Usuario",
    # UI message
    "language": "Idioma",
    "add_match": "Nuevo partido",
    "add_player": "Nuevo jugador",
    "check_player": "Ficha del jugador",
    "check_team": "Ficha del equipo",
    "match_history": "Historial de partidos",
    "last_match_history": "Historial de los últimos partidos",
    "billboard": "Clasificación",
    "overview": "Vista general",
    "matches": "Partidos",
    "analytics": "Análisis",
    "administration": "Administración",
    "submit": "Enviar",
    "ranking": "Clasificación",
    "players_teams": "Jugadores/Equipos",
    "players_table": "Tabla de jugadores",
    "team": "Equipo",
    "team1": "Equipo 1",
    "team2": "Equipo 2",
    "player": "Jugador",
    "player1": "Jugador 1",
    "player2": "Jugador 2",
    "time": "Hora",
    "match_added_success": "¡Partido registrado!",
    "match_added_error": "No se pudo agregar el partido, error desconocido",
    "match_exists_error": "El partido ya ha sido registrado",
    "match_not_finished_error": "Los cálculos no cuadran, el marcador no coincide",
    "see_updated_elo_below": "Aquí están los nuevos puntos Elo:",
    "player_added_success": " ha sido añadido con éxito!",
    "player_added_error": "No se pudo agregar el jugador, error desconocido:",
    "player_exists_error": " ya ha sido registrado",
    "player_invalid_name_error": " no es un nombre válido. Asegúrate de que tenga al menos 2 caracteres, sin números y que sea un verdadero nombre de campeón.",
    "player_not_selected_error": "Asegúrate de haber seleccionado todos los jugadores",
    "player_deletion_error": "Error al eliminar el jugador:",
    "team_same_player_error": "El mismo jugador ha sido seleccionado en el mismo equipo, ¡1 contra 2 no es justo!",
    "team_not_found_error": "Este equipo nunca ha jugado un partido juntos. Tal vez sea una pena, pero no hay nada que mostrar.",
    "same_player_in_both_teams_error": "Un jugador está presente en ambos equipos al mismo tiempo, ¡difícil estar en dos sitios a la vez!",
    "next_feature": "PRÓXIMAMENTE",
    "ranking_evolution": "Evolución del ranking",
    "ranking_evolution_over_x_last_matches": "Evolución del ranking en los últimos {x} partidos",
    "result": "Resultado",
    "victory": "Victoria",
    "defeat": "Derrota",
    "ratio_vd": "V/D",
    "nb_won_games_diff": "Diferencia de juegos ganados",
    "metric": "Métrica",
    "evolution": "Evolución",
    "creation_date": "Fecha de creación",
    "player_relationships": "Espíritu de equipo",
    "best_teammate": "Mejor compañero",
    "x_victories_together": "{x} victorias juntos",
    "most_teammate": "Compañero de confianza",
    "x_matches_together": "{x} partidos juntos",
    "black_beast": "Bestia negra",
    "x_defeats_against": "{x} derrotas contra él/ella",
    "black_beasts": "Bestias negras",
    "x_defeats_against_them": "{x} derrotas contra ellos/ellas",
    "favorite_victim": "Víctima favorita",
    "x_victories_against": "{x} victorias contra él/ella",
    "favorite_victims": "Víctimas favoritas",
    "x_victories_against_them": "{x} victorias contra ellos/ellas",
    "no_league_database_error": "No hay ninguna liga para mostrar por el momento. Registra una liga en la página 'Nueva liga'.",
    "no_match_database_error": "No hay ningún partido en esta liga por el momento. Asegúrate de registrar a tus primeros jugadores en la página 'Nuevo jugador', luego ingresa tu primer partido en la página 'Nuevo partido'.",
    "not_enough_players_database_error": "Todavía no hay suficientes jugadores registrados en esta liga para jugar un partido. Asegúrate de haber creado al menos 4 jugadores en la página 'Nuevo jugador'.",
    "check_logs": "Consultar registros",
    "delete_player": "Eliminar un jugador",
    "delete_match": "Eliminar un partido",
    "delete": "Eliminar",
    "player_deleted": " ha sido eliminado. Adiós 😢",
    "player_already_deleted": " ya ha sido eliminado, deja de insistir, ya fue lo suficientemente doloroso 😭",
    "all_players_not_in_league_error": "Hay jugadores que no pertenecen a la liga. Asegúrate de que todos los campeones sean parte de la misma liga para registrar un partido juntos.",
    "add_league": "Nueva liga",
    "league_added_success": " ha sido añadida con éxito.",
    "league_exists_error": " ya está registrada.",
    "league_invalid_name_error": " no es un nombre de liga válido. Asegúrate de que tenga al menos 2 caracteres, sin números y que represente un verdadero nombre de liga de campeones.",
    "league_added_error": " No se pudo agregar la liga, error desconocido:",
    "assign_league": "Asignar a una liga",
    "player_already_in_league_error": " ya está registrado en la liga ",
    "assigned_league_to_player_success": " ha sido registrado en la liga ",
    "time_scale": "Escala de tiempo",
    "time_scale_help_message": "Muestra el tiempo real entre los partidos en el gráfico",
    "welcome_not_logged": "¡Bienvenido a Padel Tracker!",
    "padel_tracker_kezako": """
        **Padel Tracker** es una pequeña aplicación que te permite registrar tus partidos de pádel y seguir tu evolución y la de tus amigos a lo largo del tiempo.    

        La aplicación incorpora un sistema de clasificación tipo Elo, ideal para su uso dentro de un grupo de jugadores habituales (*Liga*).  
        También te permite analizar tu rendimiento con diferentes compañeros de liga, útil para identificar qué parejas funcionan bien juntas (o no... 😬).
        El sistema de clasificación tiene en cuenta la diferencia de juegos ganados entre los dos equipos. Así que, incluso si van perdiendo 5-0, no se rindan: ¡cada punto cuenta!

        - ¿Quién será el campeón de tu liga?  
        - ¿Quién será el compañero ideal con el que arrasas en la cancha?  
        - ¿Quién será el último en la clasificación y tendrá que pagar la ronda en el próximo partido?  

        Para iniciar sesión, tienes varias opciones:
        - Crear una cuenta / iniciar sesión con un correo y contraseña estándar.  
          (_La aplicación utiliza [`Auth0`](http://www.auth0.com) para la autenticación. Si recibes correos con ese nombre, no te preocupes._)    
        - También puedes iniciar sesión rápidamente con una cuenta de `Google`.  
            _(La aplicación no usa tus datos personales más allá de almacenar un identificador único para reconocerte la próxima vez)._  

        Proyecto de código abierto, más información en el [repositorio de GitHub del proyecto](https://github.com/poulpe/padel-tracker).
    """,
    "click_to_login": "Haz clic abajo para iniciar sesión o registrarte",
    "login_signup": "Iniciar sesión / Registrarse",
    "login": "Iniciar sesión",
    "click_to_connect_as_guest": "Si eres tímido, solo puedes echar un vistazo",
    "connect_as_guest": "Iniciar sesión como invitado",
    "my_account": "Mi cuenta",
    "manage_account": "Administrar mi cuenta",
    "logout": "Cerrar sesión",
    "finalize_signup": "¡Bienvenido, campeón! Finaliza tu registro",
    "existing_league": "Liga",
    "existing_league_message": "¿Tu liga ya existe y quieres unirte? Déjalo en blanco si no.",
    "finalize_signup_existing_player_message_header": "¿Tal vez ya has sido agregado como jugador?",
    "finalize_signup_existing_player_message_sub": "Si te reconoces, puedes asignarte:",
    "finalize_signup_not_existing_player_message_header": "¿No te encontraste arriba?",
    "finalize_signup_not_existing_player_message_sub": "Entonces, este es tu lugar:",
    "existing_player": "En realidad, soy yo:",
    "username_help": "¡Debe ser un nombre de campeón! Solo sin caracteres especiales ni números.",
    "user_added_success": "¡Genial! Tu cuenta se está creando.",
    "existing_league_help": "¿Tu liga ya existe y quieres unirte? Déjalo en blanco si no. Siempre podrás crear/unirte a una liga más tarde desde el menú.",
    "join_league": "Unirse a una liga",
    "feedback_header": "Formulario de comentarios",
    "feedback_button": "¿Un error? ¿Una solicitud?",
    "feedback_subheader_line1": "¿Un error?",
    "feedback_subheader_line2": "¿Una mejora que te gustaría o una solicitud específica?",
    "feedback_subsubheader": """
        ¡No dudes en compartir tu opinión!     
        _(Aunque solo sea para quejarte de esos malditos bugs o para agradecerme porque encuentras la app genial!)_
    """,
    "feedback_title": "Título",
    "feedback_description": "Descripción",
    "feedback_submit_success": """
        ¡Mensaje enviado con éxito, gracias por tu comentario!  
        Si quieres hacer seguimiento del problema: """,
    "feedback_submit_error": "Error al enviar el comentario, esta app definitivamente está llena de bugs...",
}


class Language(StrEnum):
    FR = "Français"
    EN = "English"
    ES = "Español"


_DICT_LANGUAGES = {
    Language.FR: _DICT_TO_FR,
    Language.EN: _DICT_TO_EN,
    Language.ES: _DICT_TO_ES,
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
            logger = get_logger("ui.languages")
            logger.error(f"translation for '{key}' in lang={str(self.lang)} is missing")
        return result


def update_session_state_translator() -> None:
    st.session_state.translator = LanguageTranslator(st.session_state.language)


DEFAULT_LANGUAGE = Language.FR
DEFAULT_TRANSLATOR = LanguageTranslator(DEFAULT_LANGUAGE)

SUPPORTED_LANGUAGES = (Language.FR, Language.EN, Language.ES)
