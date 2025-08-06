import sys
import logging

from sqlmodel import SQLModel
from alembic import context

from padel_tracker import models as models
from padel_tracker.database.db import DB, DICT_CONF

DB_MODE = DICT_CONF["general"]["db_mode"]
RUN_MODE = DICT_CONF["general"]["run_mode"]

# Configure loggings
## Formatter
formatter = logging.Formatter(
    "%(levelname)-5.5s [%(name)s] %(message)s", datefmt="%H:%M:%S"
)
## Handler
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.NOTSET)
console_handler.setFormatter(formatter)
## Root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)
root_logger.addHandler(console_handler)
## SQLAlchemy logger (without handler, will propagate to root)
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.WARNING)
## Alembic logger (without handler, will propagate to root)
alembic_logger = logging.getLogger("alembic")
alembic_logger.setLevel(logging.INFO)


def include_object(object, name, type_, reflected, compare_to):
    """
    Function to filter objects in the metadata reflection.
    - Only include tables from the "public" schema.
    - Exclude all other schemas.
    """
    # print(object)
    # print(name)
    # print(type_)
    if type_ == "table":
        # print(object.__dict__)
        return name not in ("teammatchlink", "playermatchlink", "playerteamlink")
    return True


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = context.get_x_argument(as_dictionary=True).get("DATABASE_URL", DB.engine.url)
    if DB_MODE == "cloud":
        context.configure(
            url=url,
            target_metadata=SQLModel.metadata,
            literal_binds=True,
            include_object=include_object,
        )
    else:
        context.configure(
            url=url,
            target_metadata=SQLModel.metadata,
            literal_binds=True,
        )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    with DB.engine.connect() as connection:
        if DB_MODE == "cloud":
            context.configure(
                connection=connection,
                target_metadata=SQLModel.metadata,
                include_object=include_object,
            )
        else:
            context.configure(
                connection=connection,
                target_metadata=SQLModel.metadata,
            )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
