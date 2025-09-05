from typing import Any

import sqlalchemy
import pandas as pd

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import UserNotFoundError, UserExistsError
from padel_tracker.utils.datetime_utils import now
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.models.players import Player
from padel_tracker.models.users import User, UserRole
from padel_tracker.services import player_manager, league_manager

LOGGER_NAME = "users"
LOGGER = get_logger(LOGGER_NAME)

# GET


def get_user_from_auth_user_id(session: Session, auth_user_id: str) -> User:
    try:
        user = read_from_db(
            User, where=User.auth_user_id == auth_user_id, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise UserNotFoundError(f"user with {auth_user_id=} not found in database")
    return user


def get_user_from_name(session: Session, name: str) -> User:
    try:
        user = read_from_db(User, where=User.name == name, unique=True, session=session)
    except sqlalchemy.exc.NoResultFound:
        raise UserNotFoundError(f"user with {name=} not found in database")
    return user


def get_all_users(session: Session, as_df: bool = False) -> list[User] | pd.DataFrame:
    return read_from_db(User, session=session, as_df=as_df)


# CREATE


def determine_default_username(dict_auth_user: dict[str, Any]) -> str:
    try:
        name = dict_auth_user["name"]
    except KeyError:
        try:
            name = dict_auth_user["nickname"]
        except KeyError:
            err_msg = "cannot determine default username, did not find 'name' or 'nickname' in user dict"
            LOGGER.error(f"{err_msg}. {dict_auth_user=}")
            raise KeyError(err_msg) from None
    # Sanitize name
    for char in [".", "@", "_", "-"]:
        name = name.replace(char, " ")
    name = Player.sanitize_name(name)
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
        Typically st.user.to_dict(), containing keys:
        - "sub", the auth_user_id
        - "email"
        - "email_verified"
        - "picture"
        - "name" valid
        - "nickname" otherwise
    username:str
        If None, will get from default determining. Otherwise will use it
    """
    logger = get_logger(f"{LOGGER_NAME}.create")

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
        logger.error(err_msg)
        raise UserExistsError(err_msg)
    # Go creation
    ## Default to None/False missing data
    if not username:
        username = determine_default_username(dict_auth_user)
    username = (username[0].upper() + username[1:]).strip()
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
        last_visit_date=now(),
        nb_visits=1,
    )
    # Commit
    commit_to_db(user, session=session)
    logger.success(f"created {user=}")
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
    LOGGER.success(log_msg)


def log_user_visit(session: Session, auth_user_id: str) -> None:
    """Update user last_visit on db + log message in db"""
    user = get_user_from_auth_user_id(session=session, auth_user_id=auth_user_id)
    user.nb_visits += 1
    user.last_visit_date = now()
    commit_to_db(user, session=session)
    log_msg = f"user '{user.name}' logged in ({auth_user_id=})"
    LOGGER.success(log_msg)


# DELETE
def delete_user(session: Session, name: str) -> None:
    logger = get_logger(f"{LOGGER_NAME}.delete")
    # Fetch user
    try:
        user = get_user_from_name(session=session, name=name)
    except UserNotFoundError:
        err_msg = f"{name} doesn't exist, cannot delete it"
        logger.error(err_msg)
        raise UserNotFoundError(err_msg)
    except Exception as exc:
        logger.exception(exc)
        raise exc
    # Perform delete
    name = user.name
    auth_user_id = user.auth_user_id
    delete_from_db(user, session=session)
    logger.success(f"deleted User({name=}, {auth_user_id=}) successfully")
