from typing import Iterable

import pandas as pd
from sqlalchemy.engine.base import Engine
from sqlmodel import SQLModel, create_engine, Session, select
import supabase

# Must keep this line below to init all SQLModel defined
from padel_tracker import models as models
from padel_tracker.utils.paths import get_absolute_path
from padel_tracker.utils.conf import DICT_CONF, DBMode, RunMode


def get_cloud_db_url(
    user: str, password: str, host: str, port: str, dbname: str
) -> str:
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"


def get_db_url(
    db_mode: DBMode = DICT_CONF["general"]["db_mode"],
    run_mode: RunMode = DICT_CONF["general"]["run_mode"],
    user: str = DICT_CONF["db_credentials"]["user"],
    password: str = DICT_CONF["db_credentials"]["password"],
    host: str = DICT_CONF["db_credentials"]["host"],
    port: str = DICT_CONF["db_credentials"]["port"],
    dbname: str = DICT_CONF["db_credentials"]["dbname"],
) -> str:
    db_mode = db_mode.lower()
    run_mode = run_mode.lower()
    if db_mode == DBMode.LOCAL:
        # Determine db_name vs modes
        db_name = "database"
        if run_mode == RunMode.TEST:
            db_name += "_test"
        elif run_mode == RunMode.DEBUG:
            db_name += "_debug"
        # Determine db_url vs modes
        if run_mode == RunMode.TEST:
            db_file = get_absolute_path(__file__, f"../../../tests/data/{db_name}.db")
            db_file.parent.mkdir(parents=True)
        else:
            db_file = get_absolute_path(__file__, f"../../../data/{db_name}.db")
        db_url = f"sqlite:///{db_file}"
    elif db_mode == DBMode.CLOUD:
        db_url = get_cloud_db_url(
            user=user, password=password, host=host, port=port, dbname=dbname
        )
    else:
        err_msg = f"invalid db_mode got from config. Got {db_mode=}. Must be 'cloud' or 'local'"
        raise ValueError(err_msg)
    return db_url


def set_db_engine(
    db_mode: DBMode = DICT_CONF["general"]["db_mode"],
    run_mode: RunMode = DICT_CONF["general"]["run_mode"],
    user: str = DICT_CONF["db_credentials"]["user"],
    password: str = DICT_CONF["db_credentials"]["password"],
    host: str = DICT_CONF["db_credentials"]["host"],
    port: str = DICT_CONF["db_credentials"]["port"],
    dbname: str = DICT_CONF["db_credentials"]["dbname"],
) -> Engine:
    # Create url based on modes
    try:
        db_url = get_db_url(
            db_mode=db_mode,
            run_mode=run_mode,
            user=user,
            password=password,
            host=host,
            port=port,
            dbname=dbname,
        )
    except ValueError:
        err_msg = f"invalid db_mode got from config. Got {db_mode=}. Must be 'cloud' or 'local'"
        raise ValueError(err_msg)
    # Create engine
    if db_mode == DBMode.CLOUD:
        connect_args = {"options": "-csearch_path=public"}
    else:
        connect_args = {}
    db_engine = create_engine(db_url, connect_args=connect_args)
    return db_engine


class Database:
    """Utils object for getting database sessions"""

    def __init__(
        self,
        db_mode: DBMode = DICT_CONF["general"]["db_mode"],
        run_mode: RunMode = DICT_CONF["general"]["run_mode"],
        user: str = DICT_CONF["db_credentials"]["user"],
        password: str = DICT_CONF["db_credentials"]["password"],
        host: str = DICT_CONF["db_credentials"]["host"],
        port: str = DICT_CONF["db_credentials"]["port"],
        dbname: str = DICT_CONF["db_credentials"]["dbname"],
    ):
        self._engine = None
        self.db_mode = db_mode
        self.run_mode = run_mode
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname

    @property
    def engine(self):
        if not self._engine:
            self._engine = set_db_engine(
                db_mode=self.db_mode,
                run_mode=self.run_mode,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                dbname=self.dbname,
            )
        return self._engine

    def get_session(self):
        return Session(self.engine)


DB = Database()


def init_db_and_tables(db: Database = DB):
    """To be called in main at init"""
    SQLModel.metadata.create_all(db.engine)


def commit_to_db_no_session(*objects, refresh: bool = True) -> None:
    with DB.get_session() as session:
        for object in objects:
            session.add(object)
        session.commit()
        if refresh:
            for object in objects:
                session.refresh(object)


def commit_to_db_session(*objects, session: Session, refresh: bool = True) -> None:
    for object in objects:
        session.add(object)
    session.commit()
    if refresh:
        for object in objects:
            session.refresh(object)


def commit_to_db(*objects, session: Session = None, refresh: bool = True) -> None:
    """Create or update objects from database

    Examples
    --------
    >>> with DB.get_session() as session:
    ...     "Create objects p1, p2 and p3"
    ...     commit_to_db(p1, p2, p3, session=session)

    >>> # If no need to access objects updated attributes after commit
    >>> "Create objects p1, p2 and p3"
    >>> commit_to_db(p1, p2, p3)
    """
    if session:
        commit_to_db_session(*objects, session=session, refresh=refresh)
    else:
        commit_to_db_no_session(*objects, refresh=refresh)


def make_read_statement(
    class_,
    where=None,
    limit_first: int = None,
    order_by=None,
    order_descending: bool = False,
    join_class=None,
    join_clause=None,
):
    statement = select(class_)
    if join_class:
        statement = statement.join(join_class, join_clause)
    if where is not None:
        if not isinstance(where, Iterable):
            statement = statement.where(where)
        else:
            for where_statement in where:
                statement = statement.where(where_statement)
    if order_by:
        if order_descending:
            statement = statement.order_by(order_by.desc())
        else:
            statement = statement.order_by(order_by)
    if limit_first:
        statement = statement.limit(limit_first)
    return statement


def read_from_db(
    class_,
    where=None,
    unique: bool = False,
    limit_first: int = None,
    limit_last: int = None,
    order_by=None,
    order_descending: bool = False,
    join_class=None,
    join_clause=None,
    session: Session = None,
    as_df: bool = False,
) -> object | list | pd.DataFrame:
    """Query database for table/class and return found object.
    Can be called within a db session if existing, without closing it, if `session` is specified.

    Examples
    --------
    >>> # Basic usage (will return all players)
    >>> read_from_db(Player)

    >>> # Filter result with a simple "where" statement
    >>> result_filter = col(Player.name) == "Patrick"
    >>> read_from_db(Player, where=result_filter)

    >>> # Filter result with a multiple AND "where" statement
    >>> result_filter = col(Player.nb_matches) >= 10, col(Player.nb_victories) >= 5
    >>> read_from_db(Player, where=result_filter)

    >>> # Filter result with a multiple OR "where" statement (use or_ from sqlmodel)
    >>> result_filter = or_(col(Player.nb_matches) >= 10, col(Player.nb_victories) >= 5)
    >>> read_from_db(Player, where=result_filter)

    >>> # Expect only one row
    >>> result_filter = col(Player.name) == "Legendary Patrick"
    >>> my_player = read_from_db(Player, where=result_filter, unique=True)

    >>> # Get list of IDS matching a list (IN_)
    >>> player_ids = [12, 56]
    >>> my_player = read_from_db(Player, where=Player.id.in_(player_ids))

    >>> # SESSION : already opened a session and want the read to be executed in this context
    >>> match_id_to_retrieve = 12
    >>> with DB.get_session() as session:
    ...     # Retrieve Match
    ...     finished_match: Match = read_from_db(
    ...         Match,
    ...         where=Match.id == match_id_to_retrieve,
    ...         unique=True,
    ...         session=session,
    ...     )
    ...     # Now do stuff with finished_match and its players
    ...     winners, losers = finished_match.get_winners_losers()
    ...     finished_match.players[0].elo_rating = 824
    ...     commit_to_db(finished_match, session=session)

    Parameters
    ----------
    class_:
        The class inherited from SQLModel (i.e : Player, Match...)
    where_req: optional
        As class_.name == "my_value"
    unique: bool, optional
        If only one is expected. Will raise specfic sqlmodel error if not exactly one.
    limit: int, optional
        To get only first "x" rows
    session: Session, optional
        Important if wanted to have variables "kept alive" in the session context manager
    as_df:bool
        Returns result under a pd.DataFrame format (using .model_dump() from SQLModel). Default is False.

    Returns
    -------
    results: list | object | pd.DataFrame
        As a list of class instances, matching with the "where" request if mentioned.
        If unique=True, will return only the object directly.
        If as_df=True, will return under a pd.DataFrame format.
    """
    # Make statement
    statement = make_read_statement(
        class_,
        where=where,
        limit_first=limit_first,
        order_by=order_by,
        order_descending=order_descending,
        join_class=join_class,
        join_clause=join_clause,
    )
    # Send read request to session
    if session is None:
        with DB.get_session() as session:
            reply = session.exec(statement)
            result = reply.one() if unique else reply.all()
    else:
        reply = session.exec(statement)
        result = reply.one() if unique else reply.all()
    if limit_last:
        result = result[-limit_last:]
    if as_df:
        if isinstance(result, list):
            result = pd.DataFrame([row.model_dump() for row in result])
        else:
            result = pd.DataFrame([result.model_dump()])
    return result


def delete_from_db(*objects, session: Session) -> None:
    for object in objects:
        session.delete(object)
    session.commit()


def create_supabase_client():
    return supabase.create_client(
        supabase_url=DICT_CONF["db_credentials"]["supabase_api_url"],
        supabase_key=DICT_CONF["db_credentials"]["supabase_api_key"],
    )
