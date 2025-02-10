from typing import Any

import sqlalchemy
import pydantic

from padel_tracker.utils.logs import get_logger
from padel_tracker.utils.errors import UserNotFoundError, UserExistsError
from padel_tracker.database.db import (
    Session,
    commit_to_db,
    read_from_db,
    delete_from_db,
)
from padel_tracker.models.players import Player
from padel_tracker.models.users import User, UserRole
from padel_tracker.services.player_manager import create_player

LOGGER = get_logger("user_manager")


def get_user_from_auth_user_id(session: Session, auth_user_id: str) -> User:
    try:
        user = read_from_db(
            User, where=User.auth_user_id == auth_user_id, unique=True, session=session
        )
    except sqlalchemy.exc.NoResultFound:
        raise UserNotFoundError(f"user with {auth_user_id=} not found in database")
    return user


def create_user_from_auth_user(
    session: Session,
    dict_auth_user: dict[str, Any],
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
    user = User(
        auth_user_id=auth_user_id,
        email=dict_auth_user["email"],
        email_verified=dict_auth_user["email_verified"],
        picture_url=dict_auth_user["picture"],
    )
    try:
        user.name = dict_auth_user["name"]
    except pydantic.ValidationError as exc:
        try:
            user.name = dict_auth_user["nickname"]
        except pydantic.ValidationError as exc:
            name = dict_auth_user["nickname"]
            for char in [".", "@", "_", "-"]:
                name = name.replace(char, " ")
            user.name = name.capitalize()
    # Commit
    commit_to_db(user, session=session)
    LOGGER.notif(f"created {user=}")
    # TODO: Also create player if specified
    # if is_create_player:
    #     create_player(session=session, name=)
    return user


def assign_player_to_user(session: Session, user: User, player: Player) -> None:
    user.player = player
    user.player_id = player.id
    if user.role == UserRole.GUEST:
        user.role = UserRole.PLAYER
    user.name = player.name
    commit_to_db(user, player, session=session)
    LOGGER.notif(f"{player=} has been assigned to {user=}")
