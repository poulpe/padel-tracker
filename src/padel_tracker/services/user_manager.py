from typing import Any

import sqlalchemy
import pydantic

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import UserNotFoundError, UserExistsError
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
)
from padel_tracker.models.players import Player
from padel_tracker.models.users import User, UserRole
from padel_tracker.services import player_manager, league_manager

LOGGER = get_logger("user_manager")


def get_user_from_auth_user_id(session: Session, auth_user_id: str) -> User:
    try:
        user = read_from_db(
            User, where=User.auth_user_id == auth_user_id, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise UserNotFoundError(f"user with {auth_user_id=} not found in database")
    return user


def determine_default_username(dict_auth_user: dict[str, Any]) -> str:
    try:
        name = dict_auth_user["name"]
    except pydantic.ValidationError:
        try:
            name = dict_auth_user["nickname"]
        except pydantic.ValidationError:
            name = dict_auth_user["nickname"]
            for char in [".", "@", "_", "-"]:
                name = name.replace(char, " ")
            name = name.capitalize()
    return name


def create_user_from_auth_user(
    session: Session,
    dict_auth_user: dict[str, Any],
    username: str = None,
    default_league_name: str = None,
    default_language: str = None,
    is_create_player: bool = True,
) -> User:
    """
    Parameters
    ----------
    session
    dict_auth_user
        Typically st.experimental_user.to_dict(), containing keys:
        - "sub", the auth_user_id
        - "email"
        - "email_verified"
        - "picture"
        - "name" valid
        - "nickname" otherwise
    username:str
        If None, will get from default determining. Otherwise will use it
    """
    # Extract auth_user_id
    try:
        auth_user_id = dict_auth_user["sub"]
    except KeyError:
        err_msg = ""
        raise KeyError(err_msg)
    # Checks doesn't exist
    try:
        user = get_user_from_auth_user_id(session=session, auth_user_id=auth_user_id)
    except UserNotFoundError:
        pass
    else:
        err_msg = f"User({user.id=}, {auth_user_id=}) already exists, won't recreate"
        LOGGER.error(err_msg)
        raise UserExistsError(err_msg)
    # Go creation
    ## Default to None/False missing data
    if not username:
        username = determine_default_username(dict_auth_user)
    for key in ["email", "picture"]:
        if key not in dict_auth_user.keys():
            dict_auth_user[key] = None
    if "email_verified" not in dict_auth_user.keys():
        dict_auth_user["email_verified"] = False
    ## Create user object
    user = User(
        auth_user_id=auth_user_id,
        email=dict_auth_user["email"],
        email_verified=dict_auth_user["email_verified"],
        picture_url=dict_auth_user["picture"],
        default_league_name=default_league_name,
        default_language=default_language,
        name=username,
    )
    # Commit
    commit_to_db(user, session=session)
    LOGGER.notif(f"created {user=}")
    # Create player if specified
    if is_create_player:
        default_league = None
        # Fetch default league if provided
        if default_league_name:
            default_league = league_manager.get_league_from_name(
                session=session, name=default_league_name
            )
        player = player_manager.create_player(
            session=session, name=username, league=default_league
        )
        assign_player_to_user(session=session, user=user, player=player)
    return user


def assign_player_to_user(session: Session, user: User, player: Player) -> None:
    user.player = player
    user.player_id = player.id
    if user.role == UserRole.GUEST:
        user.role = UserRole.PLAYER
    user.name = player.name
    commit_to_db(user, player, session=session)
    log_msg = f"Player(name={player.name}, id={player.id}) has been assigned to User(id={user.id}, player_id={user.player_id}, email={user.email})"
    LOGGER.notif(log_msg)
