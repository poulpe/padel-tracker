from enum import StrEnum
from dataclasses import dataclass

import streamlit as st

from padel_tracker.utils.logs import get_logger


class Language(StrEnum):
    FR = "Français"
    EN = "English"
    ES = "Español"


_DICT_LANGUAGES = {
    "about_and_feedback": {
        Language.FR: "À propos & Feedback",
        Language.EN: "About & Feedback",
        Language.ES: "About & Feedback",
    },
    "match_added_error": {
        Language.FR: " Impossible d'ajouter le match, erreur inconnue",
        Language.EN: " Unknown error during match creation",
        Language.ES: "No se pudo agregar el partido, error desconocido",
    },
    "player_not_selected_error": {
        Language.FR: " Assure toi d'avoir selectionné tous les joueurs",
        Language.EN: "Make sure all players have been selected",
        Language.ES: "Asegúrate de haber seleccionado todos los jugadores",
    },
    "x_matches_together": {
        Language.FR: "{x} matchs ensemble",
        Language.EN: "{x} matches together",
        Language.ES: "{x} partidos juntos",
    },
    "add_league": {
        Language.FR: "Nouvelle ligue",
        Language.EN: "Add league",
        Language.ES: "Nueva liga",
    },
    "add_league_message": {
        Language.FR: "Créer une nouvelle ligue dont tu seras le boss",
        Language.EN: "Create a new league where you will be the boss",
        Language.ES: "Crear una nueva liga en la que serás el jefe",
    },
    "add_league_long_message": {
        Language.FR: "Créer une nouvelle ligue dont tu seras l'admin et dans laquelle tu pourras ajouter des joueurs via la page 'Gérer la ligue'",
        Language.EN: "Create a new league where you will be the admin and you can add players via the 'Manage league' page",
        Language.ES: "Crear una nueva liga de la que serás el administrador y en la que podrás añadir jugadores a través de la página 'Gestionar la liga'",
    },
    "finalize_signup_not_existing_player_message_sub": {
        Language.FR: "C'est ici que ça se passe alors:",
        Language.EN: "Then this is the place for you:",
        Language.ES: "Entonces, este es tu lugar:",
    },
    "players_same_category_message_x_points": {
        Language.FR: "Joueurs de la ligue avec un Elo similaire (+/- {x} points)",
        Language.EN: "Players from the league with a similar Elo rating (+/- {x})",
        Language.ES: "Jugadores de la liga con un Elo similar (+/- {x} puntos)",
    },
    "no_match_database_error": {
        Language.FR: "Il n'y a aucun match dans cette ligue pour le moment. Assure toi de rentrer tes premiers joueurs via la page 'Gérer la ligue -> Nouveau joueur', puis ton premier match via la page 'Nouveau match'.",
        Language.EN: "There's no match in this league at the moment. Ensure your players are declared via the page 'Manage League -> New player' and enter your first match via the page 'New match'.",
        Language.ES: "No hay ningún partido en esta liga por el momento. Asegúrate de registrar a tus primeros jugadores en la página 'Nuevo jugador', luego ingresa tu primer partido en la página 'Nuevo partido'.",
    },
    "match_not_finished_error": {
        Language.FR: "Les calculs sont pas bons Kévin, le score ne colle pas",
        Language.EN: "Scores are not valid for a finished match, please double check",
        Language.ES: "Los cálculos no cuadran, el marcador no coincide",
    },
    "no_league_database_error": {
        Language.FR: "Il n'y a aucune ligue à afficher pour le moment. Enregistre une ligue via la page 'Nouvelle ligue'",
        Language.EN: "No league for the moment. Register a first league via the page 'New league'",
        Language.ES: "No hay ninguna liga para mostrar por el momento. Registra una liga en la página 'Nueva liga'.",
    },
    "download_data_as_csv": {
        Language.FR: "Télécharger mes données en .csv",
        Language.EN: "Download data as .csv",
        Language.ES: "Descargar datos como .csv",
    },
    "time_scale": {
        Language.FR: "Échelle temps",
        Language.EN: "Time scale",
        Language.ES: "Escala de tiempo",
    },
    "player_removed": {
        Language.FR: " a été retiré. Bye bye 😢",
        Language.EN: " has been removed. Bye bye 😢",
        Language.ES: " ha sido eliminado. Adiós 😢",
    },
    "player_relationships": {
        Language.FR: "Esprit d'équipe",
        Language.EN: "Team spirit",
        Language.ES: "Espíritu de equipo",
    },
    "player": {Language.FR: "Joueur", Language.EN: "Player", Language.ES: "Jugador"},
    "ranking_evolution_over_x_last_matches": {
        Language.FR: "Évolution du classement sur les {x} derniers matchs",
        Language.EN: "Ranking evolution over the {x} last matches",
        Language.ES: "Evolución del ranking en los últimos {x} partidos",
    },
    "team2": {Language.FR: "Équipe 2", Language.EN: "Team 2", Language.ES: "Equipo 2"},
    "click_to_login": {
        Language.FR: "Clique ci dessous pour t'identifier ou t'inscrire",
        Language.EN: "Click below to log in or sign up",
        Language.ES: "Haz clic abajo para iniciar sesión o registrarte",
    },
    "feedback_title": {
        Language.FR: "Titre",
        Language.EN: "Title",
        Language.ES: "Título",
    },
    "feedback_subheader_line1": {
        Language.FR: "Un bug ?",
        Language.EN: "A bug?",
        Language.ES: "¿Un error?",
    },
    "remove_from_league": {
        Language.FR: "Retire un joueur de la ligue",
        Language.EN: "Remove a player from the league",
        Language.ES: "Eliminar un jugador de la liga",
    },
    "match_deletion_error": {
        Language.FR: "Erreur pendant la suppression du match: ",
        Language.EN: "Erro during match deletion: ",
        # Language.ES: None,
    },
    "players_same_category": {
        Language.FR: "Joueurs dans la même catégorie",
        Language.EN: "Similar players",
        Language.ES: "Jugadores similares",
    },
    "add_player_in_league": {
        Language.FR: "Nouveau joueur dans la ligue",
        Language.EN: "Add player in league",
        # Language.ES: None,
    },
    "players_teams": {
        Language.FR: "Joueurs/Équipes",
        Language.EN: "Players/Teams",
        Language.ES: "Jugadores/Equipos",
    },
    "ranking_evolution": {
        Language.FR: "Évolution du classement",
        Language.EN: "Ranking evolution",
        Language.ES: "Evolución del ranking",
    },
    "team_not_found_error": {
        Language.FR: " Cette équipe n'a jamais joué un match ensemble. C'est peut-etre dommage, mais en tout cas y'a rien à afficher",
        Language.EN: " This team has never played a match together. Maybe a pity... but anyway, there's nothing to display !",
        Language.ES: "Este equipo nunca ha jugado un partido juntos. Tal vez sea una pena, pero no hay nada que mostrar.",
    },
    "delete_match_from_id": {
        Language.FR: "Supprimer directement depuis l'ID",
        Language.EN: "Delete match from ID",
        # Language.ES: None,
    },
    "player_deletion_error": {
        Language.FR: "Erreur pendant la suppression du joueur: ",
        Language.EN: "Unexpected error during player deletion: ",
        Language.ES: "Error al eliminar el jugador:",
    },
    "language": {Language.FR: "Langue", Language.EN: "Language", Language.ES: "Idioma"},
    "my_league": {
        Language.FR: "Ma ligue",
        Language.EN: "My League",
        Language.ES: "Mi liga",
    },
    "elo_rating": {
        Language.FR: "Points Elo",
        Language.EN: "Elo rating",
        Language.ES: "Puntos Elo",
    },
    "add_player": {
        Language.FR: "Nouveau joueur",
        Language.EN: "Add player",
        Language.ES: "Nuevo jugador",
    },
    "best_rank": {
        Language.FR: "Meilleur rang",
        Language.EN: "Best rank",
        Language.ES: "Mejor rango",
    },
    "change_league_description": {
        Language.FR: "Changer la description",
        Language.EN: "Change league description",
        Language.ES: "Actualizar la descripción",
    },
    "assigned_league_to_player_success": {
        Language.FR: " a bien été enregistré dans la ligue ",
        Language.EN: " has been successfully assigned in the league ",
        Language.ES: " ha sido registrado en la liga ",
    },
    "about": {
        Language.FR: "À propos de l'appli",
        Language.EN: "About Padel Tracker",
        Language.ES: "Sobre Padel Tracker",
    },
    "finalize_signup_not_existing_player_message_header": {
        Language.FR: "Tu ne t'es pas trouvé(e) au dessus ?",
        Language.EN: "Didn't find yourself above?",
        Language.ES: "¿No te encontraste arriba?",
    },
    "user": {Language.FR: "Utilisateur", Language.EN: "User", Language.ES: "Usuario"},
    "tournament": {
        Language.FR: "Tournoi",
        Language.EN: "Tournament",
        Language.ES: "Torneo",
    },
    "evolution": {
        Language.FR: "Évolution",
        Language.EN: "Evolution",
        Language.ES: "Evolución",
    },
    "x_victories_against_them": {
        Language.FR: "{x} victoires contre eux/elles",
        Language.EN: "{x} victories against them",
        Language.ES: "{x} victorias contra ellos/ellas",
    },
    "nb_defeats": {Language.FR: "D", Language.EN: "D", Language.ES: "D"},
    "result": {
        Language.FR: "Résultat",
        Language.EN: "Result",
        Language.ES: "Resultado",
    },
    "my_account": {
        Language.FR: "Mon compte",
        Language.EN: "My account",
        Language.ES: "Mi cuenta",
    },
    "player1": {
        Language.FR: "Joueur 1",
        Language.EN: "Player 1",
        Language.ES: "Jugador 1",
    },
    "player_already_deleted": {
        Language.FR: " a déja été supprimé, arrête de t'acharner, c'était suffisant douloureux comme ça 😭",
        Language.EN: " has already been deleted, please stop, it was already painful enough 😭",
        Language.ES: " ya ha sido eliminado, deja de insistir, ya fue lo suficientemente doloroso 😭",
    },
    "user_added_error": {
        Language.FR: "Oups, problème durant la création du compte",
        Language.EN: "Oops, an issue occurred during the account creation",
        # Language.ES: None
    },
    "last_match_history": {
        Language.FR: "Historique des derniers matchs",
        Language.EN: "Last matches history",
        Language.ES: "Historial de los últimos partidos",
    },
    "logout": {
        Language.FR: "Se déconnecter",
        Language.EN: "Log out",
        Language.ES: "Cerrar sesión",
    },
    "finalize_signup_existing_player_message_header": {
        Language.FR: "Peut-être que tu as déja été ajouté en tant que joueur ?",
        Language.EN: "Maybe you've already been added as a player ?",
        Language.ES: "¿Tal vez ya has sido agregado como jugador?",
    },
    "player2": {
        Language.FR: "Joueur 2",
        Language.EN: "Player 2",
        Language.ES: "Jugador 2",
    },
    "all_players_not_in_league_error": {
        Language.FR: "Il y a des joueurs qui ne font pas parties de la ligue, assure toi que tous tes champions font bien partie de la meme ligue pour enregistrer un match ensemble.",
        Language.EN: "Some/all players are not part of the league, make sure they are part of the league so you can register a match together",
        Language.ES: "Hay jugadores que no pertenecen a la liga. Asegúrate de que todos los campeones sean parte de la misma liga para registrar un partido juntos.",
    },
    "nb_players": {
        Language.FR: "Nombre de joueurs",
        Language.EN: "Number of players",
        Language.ES: "Número de jugadores",
    },
    "nb_won_games_diff": {
        Language.FR: "Différence de jeux gagnés",
        Language.EN: "Won games difference",
        Language.ES: "Diferencia de juegos ganados",
    },
    "match_history": {
        Language.FR: "Historique des matchs",
        Language.EN: "Match history",
        Language.ES: "Historial de partidos",
    },
    "existing_player": {
        Language.FR: "En fait, c'est moi:",
        Language.EN: "Actually, that's me:",
        Language.ES: "En realidad, soy yo:",
    },
    "league_exists_error": {
        Language.FR: " a déja été enregistré",
        Language.EN: " has already been added",
        Language.ES: " ya está registrada.",
    },
    "favorite_victims": {
        Language.FR: "Victimes préférées",
        Language.EN: "Favorite victims",
        Language.ES: "Víctimas favoritas",
    },
    "league_invalid_name_error": {
        Language.FR: " n'est pas un nom de ligue valide. Assure toi qu'il contient au moins 2 caractères, pas de chiffres et qu'il représente un vrai nom de ligue de batard !",
        Language.EN: " is not a valid league name. Make sure it has at least 2 alphabetical characters, no number and that it represents a valid champion's league name !",
        Language.ES: " no es un nombre de liga válido. Asegúrate de que tenga al menos 2 caracteres, sin números y que represente un verdadero nombre de liga de campeones.",
    },
    "public_league": {
        Language.FR: "Ligue publique",
        Language.EN: "Public League",
        Language.ES: "Liga pública",
    },
    "league_names": {
        Language.FR: "Ligues",
        Language.EN: "Leagues",
        Language.ES: "Ligas",
    },
    "user_added_success": {
        Language.FR: "Nickel, ton compte est en cours de création !",
        Language.EN: "Great! Your account is being created!",
        Language.ES: "¡Genial! Tu cuenta se está creando.",
    },
    "delete_match": {
        Language.FR: "Supprimer un match",
        Language.EN: "Delete match",
        Language.ES: "Eliminar un partido",
    },
    "join_league": {
        Language.FR: "Rejoindre une ligue",
        Language.EN: "Join a league",
        Language.ES: "Unirse a una liga",
    },
    "not_enough_players_database_error": {
        Language.FR: "Il n'y a pas encore assez de joueurs enregistrés dans cette ligue pour faire un match. Assure toi d'avoir créé au moins 4 joueurs via la page 'Gérer la ligue -> Nouveau joueur'.",
        Language.EN: "Not enough players yet registered in this league to make a match. Ensure you've created at least 4 players via the page 'Manage league -> New player'.",
        Language.ES: "Todavía no hay suficientes jugadores registrados en esta liga para jugar un partido. Asegúrate de haber creado al menos 4 jugadores en la página 'Nuevo jugador'.",
    },
    "player_exists_error": {
        Language.FR: " a déja été enregistré",
        Language.EN: " has already been added",
        Language.ES: " ya ha sido registrado",
    },
    "existing_league": {
        Language.FR: "Ligue",
        Language.EN: "League",
        Language.ES: "Liga",
    },
    "player_already_in_league_error": {
        Language.FR: "  a déja été enregistré dans la ligue ",
        Language.EN: "  has already been assigned to this league",
        Language.ES: " ya está registrado en la liga ",
    },
    "next_feature": {
        Language.FR: "BIENTOT",
        Language.EN: "SOON",
        Language.ES: "PRÓXIMAMENTE",
    },
    "black_beasts": {
        Language.FR: "Bêtes noires",
        Language.EN: "Black beasts",
        Language.ES: "Bestias negras",
    },
    "favorite_victim": {
        Language.FR: "Victime préférée",
        Language.EN: "Favorite victim",
        Language.ES: "Víctima favorita",
    },
    "name": {Language.FR: "Nom", Language.EN: "Name", Language.ES: "Nombre"},
    "feedback_submit_error": {
        Language.FR: "Problème durant l'envoi du feedback, cette appli est definitivement buggée du cul...",
        Language.EN: "Error while sending feedback, this app is definitely buggy as hell...",
        Language.ES: "Error al enviar el comentario, esta app definitivamente está llena de bugs...",
    },
    "player_added_error": {
        Language.FR: " Impossible d'ajouter le joueur, erreur inconnue:",
        Language.EN: " Unknown error during player creation:",
        Language.ES: " No se pudo agregar el jugador, error desconocido:",
    },
    "rank": {Language.FR: "Rang", Language.EN: "Rank", Language.ES: "Rango"},
    "end_date": {Language.FR: "Fin", Language.EN: "End", Language.ES: "Final"},
    "players_table": {
        Language.FR: "Tableau des joueurs",
        Language.EN: "Players table",
        Language.ES: "Tabla de jugadores",
    },
    "padel_tracker_kezako": {
        Language.FR: """
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
        Language.EN: """
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
        Language.ES: """
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
    },
    "feedback_inputs_error": {
        Language.FR: "Assure toi d'avoir rempli le Titre et la Description",
        Language.EN: "Ensure 'Title' and 'Description' are well fulfilled",
        Language.ES: "Asegurarse de que 'Título' y 'Descripción' están bien cumplidos",
    },
    "team_name": {Language.FR: "Équipe", Language.EN: "Team", Language.ES: "Equipo"},
    "elo_rating_history": {
        Language.FR: "Historique des points Elo",
        Language.EN: "Elo rating history",
        Language.ES: "Historial de Elo",
    },
    "overview": {
        Language.FR: "Vue générale",
        Language.EN: "Overview",
        Language.ES: "Vista general",
    },
    "click_to_connect_as_guest": {
        Language.FR: "Si t'es timide, tu peux juste venir y jeter un oeil comme ça",
        Language.EN: "If you're feeling shy, you can just take a look around",
        Language.ES: "Si eres tímido, solo puedes echar un vistazo",
    },
    "league_added_success": {
        Language.FR: " a été ajouté avec succès !",
        Language.EN: " added successfully !",
        Language.ES: " ha sido añadida con éxito.",
    },
    "player_added_success": {
        Language.FR: " a été ajouté avec succès !",
        Language.EN: " added successfully !",
        Language.ES: " ha sido añadido con éxito!",
    },
    "player_name": {
        Language.FR: "Joueur",
        Language.EN: "Player",
        Language.ES: "Jugador",
    },
    "time": {Language.FR: "Heure", Language.EN: "Time", Language.ES: "Hora"},
    "administration": {
        Language.FR: "Administration",
        Language.EN: "Administration",
        Language.ES: "Administración",
    },
    "finalize_signup_existing_player_message_sub": {
        Language.FR: "Si tu te reconnais, tu peux t'assigner:",
        Language.EN: "If you recognize yourself, you can assign yourself:",
        Language.ES: "Si te reconoces, puedes asignarte:",
    },
    "add_match": {
        Language.FR: "Nouveau match",
        Language.EN: "Add match",
        Language.ES: "Nuevo partido",
    },
    "check_team": {
        Language.FR: "Fiche d'équipe",
        Language.EN: "Check team",
        Language.ES: "Ficha del equipo",
    },
    "login": {
        Language.FR: "Se connecter",
        Language.EN: "Log in",
        Language.ES: "Iniciar sesión",
    },
    "best_teammate": {
        Language.FR: "Meilleur partenaire",
        Language.EN: "Best teammate",
        Language.ES: "Mejor compañero",
    },
    "defeat": {Language.FR: "Défaite", Language.EN: "Defeat", Language.ES: "Derrota"},
    "creation_date": {
        Language.FR: "Date d'ajout",
        Language.EN: "Creation date",
        Language.ES: "Fecha de creación",
    },
    "analytics": {
        Language.FR: "Analytics",
        Language.EN: "Analytics",
        Language.ES: "Análisis",
    },
    "feedback_description": {
        Language.FR: "Description",
        Language.EN: "Description",
        Language.ES: "Descripción",
    },
    "x_defeats_against_them": {
        Language.FR: "{x} défaites contre eux/elles",
        Language.EN: "{x} defeats against them",
        Language.ES: "{x} derrotas contra ellos/ellas",
    },
    "finalize_signup": {
        Language.FR: "Bienvenue Champion(ne), finalise ton inscription !",
        Language.EN: "Welcome Champion, finalize your registration !",
        Language.ES: "¡Bienvenido, campeón! Finaliza tu registro",
    },
    "match_added_success": {
        Language.FR: " Match enregistré !",
        Language.EN: " Match added successfully !",
        Language.ES: "¡Partido registrado!",
    },
    "manage_account": {
        Language.FR: "Gérer mon compte",
        Language.EN: "Manage my account",
        Language.ES: "Administrar mi cuenta",
    },
    "nb_victories": {Language.FR: "V", Language.EN: "V", Language.ES: "V"},
    "feedback_header": {
        Language.FR: "Formulaire de feedback",
        Language.EN: "Feedback Form",
        Language.ES: "Formulario de comentarios",
    },
    "delete": {Language.FR: "Supprime", Language.EN: "Delete", Language.ES: "Eliminar"},
    "username_help": {
        Language.FR: "Faut que ce soit un putain de nom de Champion ! Idéalement à consonnance espagnole donc... Juste pas de caractères spéciaux, ni de chiffres",
        Language.EN: "It has to be a badass Champion name! Ideally, something Spanish-sounding… Just no special characters or numbers",
        Language.ES: "¡Debe ser un nombre de campeón! Solo sin caracteres especiales ni números.",
    },
    "add_existing_in_league": {
        Language.FR: "Recrute un joueur existant",
        Language.EN: "Recruit existing player",
        Language.ES: "Reclutar existente jugador",
    },
    "feedback_button": {
        Language.FR: "Un bug ? Une demande ?",
        Language.EN: "A bug? A request?",
        Language.ES: "¿Un error? ¿Una solicitud?",
    },
    "match_deleted": {
        Language.FR: "Le match a été supprimé",
        Language.EN: "Match has been deleted",
        Language.ES: "El partido ha sido eliminado",
    },
    "league_added_error": {
        Language.FR: " Impossible d'ajouter la ligue, erreur inconnue:",
        Language.EN: " Unknown error during league creation:",
        Language.ES: " No se pudo agregar la liga, error desconocido:",
    },
    "friendly_match_help": {
        Language.FR: "Un match amical n'update pas le classement Elo (seulement le nombre de matchs/victoires/défaites)",
        Language.EN: "A friendly match doesn't update the Elo ranking (only the number of matches/wins/losses)",
        Language.ES: "Un partido amistoso no actualiza la clasificación Elo (solo el número de partidos/victorias/derrotas)",
    },
    "delete_player": {
        Language.FR: "Supprimer un joueur",
        Language.EN: "Delete player",
        Language.ES: "Eliminar un jugador",
    },
    "retrieve_match": {
        Language.FR: "Retrouver un match",
        Language.EN: "Retrieve a match",
        Language.ES: "Buscar a un partido",
    },
    "matches": {Language.FR: "Matchs", Language.EN: "Matches", Language.ES: "Partidos"},
    "friendly_match": {
        Language.FR: "Match amical",
        Language.EN: "Friendly match",
        Language.ES: "Partido amistoso",
    },
    "team": {Language.FR: "Équipe", Language.EN: "Team", Language.ES: "Equipo"},
    "private_league": {
        Language.FR: "Ligue privée",
        Language.EN: "Private League",
        Language.ES: "Liga privada",
    },
    "black_beast": {
        Language.FR: "Bête noire",
        Language.EN: "Black beast",
        Language.ES: "Bestia negra",
    },
    "assign_league": {
        Language.FR: "Recrute dans une ligue",
        Language.EN: "Assign player to league",
        Language.ES: "Asignar a una liga",
    },
    "manage_league": {
        Language.FR: "Gérer la ligue",
        Language.EN: "Manage League",
        Language.ES: "Gestionar la liga",
    },
    "last_match_date": {
        Language.FR: "Dernier match",
        Language.EN: "Last match",
        Language.ES: "Último partido",
    },
    "join_existing_league":{
        Language.FR: "Rejoindre une ligue existante",
        Language.EN: "Join existing league",
        Language.ES: "Unirte a una existente liga",
    },
    "join_existing_league_help": {
        Language.FR: "Ta ligue existe déja et tu souhaites la rejoindre ? Laisse vide sinon. Tu pourras toujours créer/rejoindre une ligue plus tard dans le menu",
        Language.EN: "Does your league already exist, and you want to join? Leave blank otherwise. You can always create/join a league later from the menu",
        Language.ES: "¿Tu liga ya existe y quieres unirte? Déjalo en blanco si no. Siempre podrás crear/unirte a una liga más tarde desde el menú.",
    },
    "join_existing_league_message": {
        Language.FR: "Ta ligue existe déja et tu souhaites la rejoindre ?",
        Language.EN: "Does your league already exist and you want to join?",
        Language.ES: "¿Tu liga ya existe y quieres unirte?",
    },
    "league_admins": {
        Language.FR: "Administrateurs de la ligue",
        Language.EN: "League Administrators",
        Language.ES: "Administradores de la liga",
    },
    "billboard": {
        Language.FR: "Billboard",
        Language.EN: "Billboard",
        Language.ES: "Clasificación",
    },
    "victory": {
        Language.FR: "Victoire",
        Language.EN: "Victory",
        Language.ES: "Victoria",
    },
    "category": {Language.FR: "Type", Language.EN: "Type", Language.ES: "Tipo"},
    "check_logs": {
        Language.FR: "Consulter les logs",
        Language.EN: "Check logs",
        Language.ES: "Consultar registros",
    },
    "login_signup": {
        Language.FR: "Se connecter / S'inscrire",
        Language.EN: "Log in / Sign up",
        Language.ES: "Iniciar sesión / Registrarse",
    },
    "metric": {Language.FR: "Métrique", Language.EN: "Metric", Language.ES: "Métrica"},
    "manage_my_league": {
        Language.FR: "Gérer ma ligue",
        Language.EN: "Manage my league",
        Language.ES: "Gestionar mi liga",
    },
    "check_player": {
        Language.FR: "Fiche de joueur",
        Language.EN: "Check player",
        Language.ES: "Ficha del jugador",
    },
    "score": {Language.FR: "Score", Language.EN: "Score", Language.ES: "Puntuación"},
    "feedback_subheader_line2": {
        Language.FR: "Une amélioration que tu aimerais ou une demande particulière ?",
        Language.EN: "An improvement you'd like or a specific request?",
        Language.ES: "¿Una mejora que te gustaría o una solicitud específica?",
    },
    "ratio_vd": {Language.FR: "V/D", Language.EN: "V/D", Language.ES: "V/D"},
    "date": {Language.FR: "Date", Language.EN: "Date", Language.ES: "Fecha"},
    "time_scale_help_message": {
        Language.FR: "Montre le temps réel entre les matchs sur le graph",
        Language.EN: "Show real time difference between matches on the graph",
        Language.ES: "Muestra el tiempo real entre los partidos en el gráfico",
    },
    "misc": {Language.FR: "Autre", Language.EN: "Misc", Language.ES: "Misceláneo"},
    "match_exists_error": {
        Language.FR: " Le match a déja été enregistré",
        Language.EN: " Match already added",
        Language.ES: "El partido ya ha sido registrado",
    },
    "best_elo_rating": {
        Language.FR: "Meilleur Elo",
        Language.EN: "Best Elo rating",
        Language.ES: "Mejor Elo",
    },
    "league": {Language.FR: "Ligue", Language.EN: "League", Language.ES: "Liga"},
    "player_invalid_name_error": {
        Language.FR: " n'est pas un nom valide. Assure toi qu'il contient au moins 2 caractères, pas de chiffres et qu'il représente un vrai nom de champion !",
        Language.EN: " is not a valid name. Make sure it has at least 2 alphabetical characters, no number and that it represents a valid champion name !",
        Language.ES: " no es un nombre válido. Asegúrate de que tenga al menos 2 caracteres, sin números y que sea un verdadero nombre de campeón.",
    },
    "match_name": {Language.FR: "Match", Language.EN: "Match", Language.ES: "Partido"},
    "nb_matches": {
        Language.FR: "Matches",
        Language.EN: "Matches",
        Language.ES: "Partidos",
    },
    "private_league_help": {
        Language.FR: "Faire en sorte que la ligue ne soit visible que pour toi et pour les joueurs que tu ajouteras manuellement via le menu 'Gérer la ligue'",
        Language.EN: "Make the league visible only to you and the players you manually add via the 'Manage League' menu.",
        Language.ES: "Haz que la liga sea visible solo para ti y para los jugadores que añadas manualmente desde el menú 'Gestionar la liga'.",
    },
    "elo_rating_gain": {
        Language.FR: "Gain de points",
        Language.EN: "Elo rating gain",
        Language.ES: "Ganancia de puntos",
    },
    "league_name": {Language.FR: "Ligue", Language.EN: "League", Language.ES: "Liga"},
    "new_league_name": {Language.FR: "Nom de la ligue", Language.EN: "League name", Language.ES: "Nombre de la Liga"},
    "feedback_subsubheader": {
        Language.FR: """
            N'hesite pas à me faire ton retour !
            _(Meme si c'est juste pour dire que tu trouves l'appli cool, on ne sait jamais !)_
        """,
        Language.EN: """
            Feel free to share your feedback!
            _(Even if it's just to rant about those damn bugs or to thank me because you find the app cool!)_
        """,
        Language.ES: """
            ¡No dudes en compartir tu opinión!
            _(Aunque solo sea para quejarte de esos malditos bugs o para agradecerme porque encuentras la app genial!)_
        """,
    },
    "feedback_submit_success": {
        Language.FR: """
            Message envoyé avec succès, merci de ton retour !
            Si tu veux consulter le suivi du problème: 
        """,
        Language.EN: """
            Message sent successfully, thanks for your feedback!
            If you want to track the issue: 
            """,
        Language.ES: """
            ¡Mensaje enviado con éxito, gracias por tu comentario!
            Si quieres hacer seguimiento del problema: 
        """,
    },
    "unknown_error_update": {
        Language.FR: "Erreur inconnue pendant la modification: ",
        Language.EN: "Unknown error while updating: ",
        Language.ES: "Error desconocido al actualizar: ",
    },
    "see_updated_elo_below": {
        Language.FR: "Voici les nouveaux points Elo:",
        Language.EN: "See updated elo ratings below:",
        Language.ES: "Aquí están los nuevos puntos Elo:",
    },
    "most_teammate": {
        Language.FR: "Partenaire de coeur",
        Language.EN: "Most played teammate",
        Language.ES: "Compañero de confianza",
    },
    "no_description_yet": {
        Language.FR: "Pas de description pour le moment...",
        Language.EN: "No description yet...",
        Language.ES: "Sin descripción por ahora...",
    },
    "same_player_in_both_teams_error": {
        Language.FR: " Un joueur est présent dans les 2 équipes en meme temps, c'est chaud de se dupliquer des 2 cotés du terrain !",
        Language.EN: " A player is in both teams, it's hard to be in 2 places at the same time",
        Language.ES: "Un jugador está presente en ambos equipos al mismo tiempo, ¡difícil estar en dos sitios a la vez!",
    },
    "welcome_not_logged": {
        Language.FR: "Bienvenue sur Padel Tracker !",
        Language.EN: "Welcome to Padel Tracker!",
        Language.ES: "¡Bienvenido a Padel Tracker!",
    },
    "team1": {Language.FR: "Équipe 1", Language.EN: "Team 1", Language.ES: "Equipo 1"},
    "ranking": {
        Language.FR: "Classement",
        Language.EN: "Ranking",
        Language.ES: "Clasificación",
    },
    "description": {
        Language.FR: "Description",
        Language.EN: "Description",
        Language.ES: "Descripción",
    },
    "connect_as_guest": {
        Language.FR: "Se connecter en tant qu'invité",
        Language.EN: "Log in as a guest",
        Language.ES: "Iniciar sesión como invitado",
    },
    "description_updated_success": {
        Language.FR: "La description a bien été modifiée",
        Language.EN: "The description has been successfully updated",
        Language.ES: "La descripción se ha actualizado correctamente",
    },
    "league_administration": {
        Language.FR: "Gestion de la ligue",
        Language.EN: "League Management",
        Language.ES: "Gestión de la liga",
    },
    "player_deleted": {
        Language.FR: " a été supprimé. Bye bye 😢",
        Language.EN: " has been deleted. Bye bye 😢",
        Language.ES: " ha sido eliminado. Adiós 😢",
    },
    "submit": {
        Language.FR: "Roule ma poule",
        Language.EN: "Submit",
        Language.ES: "Enviar",
    },
    "submit_2": {
        Language.FR: "C'est parti",
        Language.EN: "Let's go",
        Language.ES: "Vamos",
    },
    "season_reset": {
        Language.FR: "Reset de fin de saison",
        Language.EN: "Season reset",
        Language.ES: "Reinicio de temporada",
    },
    "leagues": {Language.FR: "Ligues", Language.EN: "Leagues", Language.ES: "Ligas"},
    "add_in_league": {
        Language.FR: "Recrute dans la ligue",
        Language.EN: "Recruit into the league",
        Language.ES: "Reclutar en la liga",
    },
    "x_defeats_against": {
        Language.FR: "{x} défaites contre lui/elle",
        Language.EN: "{x} defeats against",
        Language.ES: "{x} derrotas contra él/ella",
    },
    "team_same_player_error": {
        Language.FR: " Le meme joueur a été sélectionné dans une meme équipe, 1v2 c'est pas fairplay !",
        Language.EN: " Same player has been selected in one team, 1v2 is not fairplay !",
        Language.ES: "El mismo jugador ha sido seleccionado en el mismo equipo, ¡1 contra 2 no es justo!",
    },
    "x_victories_together": {
        Language.FR: "{x} victoires ensemble",
        Language.EN: "{x} victories together",
        Language.ES: "{x} victorias juntos",
    },
    "x_victories_against": {
        Language.FR: "{x} victoires contre lui/elle",
        Language.EN: "{x} victories against",
        Language.ES: "{x} victorias contra él/ella",
    },
}


@dataclass  # For hashable compatibility with streamlit st.cache_data
class LanguageTranslator:
    lang: str | Language

    def __post_init__(self):
        self.dict_lang = _DICT_LANGUAGES

    def __call__(self, key: str):
        try:
            result = self.dict_lang[key][self.lang]
            if not result:  # If "" or None
                raise KeyError
        except KeyError:
            result = key[0].upper() + key[1:].replace("_", " ") if key else key
            logger = get_logger("ui.languages")
            logger.error(f"translation for '{key}' in lang={str(self.lang)} is missing")
        return result


DEFAULT_LANGUAGE = Language.FR
DEFAULT_TRANSLATOR = LanguageTranslator(DEFAULT_LANGUAGE)

SUPPORTED_LANGUAGES = (Language.FR, Language.EN, Language.ES)


def update_session_state_translator() -> None:
    st.session_state.translator = LanguageTranslator(st.session_state.language)


def get_translator() -> LanguageTranslator:
    """Returns st.session_state.translator and set default one if not defined yet"""
    if "translator" not in st.session_state.keys():
        st.session_state.translator = DEFAULT_TRANSLATOR
    return st.session_state.translator
