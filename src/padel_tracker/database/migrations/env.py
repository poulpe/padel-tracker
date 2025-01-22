from logging.config import fileConfig

from sqlmodel import SQLModel
from alembic import context

from padel_tracker import models as models
from padel_tracker.database.db import DB

# this is the Alembic Config object, which provides
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = context.get_x_argument(as_dictionary=True).get("DATABASE_URL", DB.engine.url)
    context.configure(url=url, target_metadata=SQLModel.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    with DB.engine.connect() as connection:
        context.configure(connection=connection, target_metadata=SQLModel.metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
