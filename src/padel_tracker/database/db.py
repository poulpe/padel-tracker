from sqlmodel import SQLModel, create_engine, Session, select

# Do this line to init all SQLModel defined
from padel_tracker import models
from padel_tracker.utils.paths import get_absolute_path

DB_PATH = get_absolute_path(__file__, "./database_try.db")
sqlite_url = f"sqlite:///{str(DB_PATH)}"

DB_ENGINE = create_engine(sqlite_url, echo=False)


def create_db_and_tables():
    """To be called in main at init"""
    SQLModel.metadata.create_all(DB_ENGINE)


def get_db_session() -> Session:
    return Session(DB_ENGINE)


def commit_to_db_no_session(*objects, refresh: bool = True) -> None:
    """Create or update objects from database
    Examples
    --------
    >>> "Create objects"
    >>> commit_to_db(p1, p2, p3)
    """
    with Session(DB_ENGINE) as session:
        for object in objects:
            session.add(object)
        session.commit()
        if refresh:
            for object in objects:
                session.refresh(object)


def commit_to_db_session(
    *objects, session: Session, refresh: bool = True, close_session: bool = False
) -> None:
    exception = None
    try:
        for object in objects:
            session.add(object)
        session.commit()
        if refresh:
            for object in objects:
                session.refresh(object)
    except Exception as exc:
        exception = exc
    finally:
        if close_session:
            session.close()
    if exception:
        session.close()
        raise exception


def commit_to_db(
    *objects, session: Session = None, close_session: bool = False, refresh: bool = True
) -> None:
    if session is None:
        commit_to_db_no_session(*objects, refresh=refresh)
    else:
        commit_to_db_session(
            *objects, session=session, refresh=refresh, close_session=close_session
        )


def make_read_statement(
    class_, where=None, limit: int = 0, order_by=None, order_descending: bool = False
):
    statement = select(class_)
    if where is not None:
        statement = statement.where(where)
    if limit:
        statement = statement.limit(limit)
    if order_by:
        if order_descending:
            statement = statement.order_by(order_by.desc())
        else:
            statement = statement.order_by(order_by)
    return statement


def read_from_db(
    class_,
    where=None,
    unique: bool = False,
    limit: int = 0,
    order_by=None,
    order_descending: bool = False,
    session: Session = None,
    close_session: bool = False,
) -> list | object:
    """Query database for table/class and return found object.
    Can be called within a db session if existing, without closing it, if `session` is specified.

    Examples
    --------
    # Basic usage (will return all players)

    >>> read_from_db(Player)

    # Filter result with a simple "where" statement

    >>> result_filter = col(Player.name) == "Patrick"
    >>> read_from_db(Player, where=result_filter)

    # Filter result with a multiple AND "where" statement

    >>> result_filter = col(Player.nb_matches) >= 10, col(Player.nb_victories) >= 5
    >>> read_from_db(Player, where=result_filter)

    # Filter result with a multiple OR "where" statement (use or_ from sqlmodel)

    >>> result_filter = or_(col(Player.nb_matches) >= 10, col(Player.nb_victories) >= 5)
    >>> read_from_db(Player, where=result_filter)

    # Expect only one row

    >>> result_filter = col(Player.name) == "Legendary Patrick"
    >>> my_player = read_from_db(Player, where=result_filter, unique=True)

    # SESSION : already opened a session and want the read to be executed in this context

    >>> match_id_to_retrieve = 12
    >>> with get_db_session() as session:
    ...     # Retrieve Match
    ...     finished_match: Match = read_from_db(
    ...         Match,
    ...         where=Match.id == match_id_to_retrieve,
    ...         unique=True,
    ...         session=session,
    ...         close_session=False,
    ...     )
    ...     # Now do stuff with finished_match and its players
    ...     winners, losers = finished_match.get_winners_losers()
    ...     finished_match.players[0].elo_rating = 824
    ...     commit_to_db(finished_match, session=session, close_session=False)

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
        Important if wanted
    close_session: bool, optional

    Returns
    -------
    results: list | object
        As a list of class instances, matching with the "where" request if mentioned.
        If unique=True, will return only the object directly.
    """
    # Make statement
    statement = make_read_statement(
        class_,
        where=where,
        limit=limit,
        order_by=order_by,
        order_descending=order_descending,
    )
    # Send read request to session
    if session is None:
        with Session(DB_ENGINE) as session:
            reply = session.exec(statement)
            result = reply.one() if unique else reply.all()
    else:
        reply = session.exec(statement)
        result = reply.one() if unique else reply.all()
        if close_session:
            session.close()
    return result


def delete_from_db(object_, session: Session, close_session: bool = False) -> None:
    session.delete(object_)
    session.commit()
    if close_session:
        session.close()
