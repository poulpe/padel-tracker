#from pathlib import Path

from sqlmodel import SQLModel, create_engine, Session, select

# Do this line to init all SQLModel defined
#from padel_tracker import models
from padel_tracker.models import hero_trials

#db_path = Path()
sqlite_file_name = "./database/database_try.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

DB_ENGINE = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(DB_ENGINE)

def commit_to_db(*objects, refresh:bool=True) -> None:
    with Session(DB_ENGINE) as session:
        for object in objects:
            session.add(object)
        session.commit()
        if refresh:
            for object in objects:
                session.refresh(object)

def read_from_db(class_, where=None) -> list:
    """

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

    Parameters
    ----------
    class_:
        The class inherited from SQLModel (i.e : Player, Match...)
    where_req: optional
        As class_.name == "my_value"

    Returns
    -------
    results:list
        As a list of class instances, matching with the "where" request if mentioned
    """
    with Session(DB_ENGINE) as session:
        statement = select(class_)
        if where is not None:
            statement = statement.where(where)
        reply = session.exec(statement)
        results = reply.all()
    return results