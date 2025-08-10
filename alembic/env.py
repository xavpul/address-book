import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from logging.config import fileConfig

from sqlalchemy import create_engine, engine_from_config, event, text
from sqlalchemy import pool

from alembic import context


from core.config import settings
from core.models import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", str(settings.DB_MIGRATION_URL))

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(
        "sqlite:///./app.db",
        poolclass=pool.NullPool,
        connect_args={"check_same_thread": False},
    )

    # 1) On each new sqlite3.Connection, enable & load the SpatiaLite extension
    def _enable_spatialite(dbapi_conn, connection_record):
        # this is a true sqlite3.Connection
        dbapi_conn.enable_load_extension(True)
        dbapi_conn.load_extension("mod_spatialite")

    event.listen(connectable, "connect", _enable_spatialite)

    # 2) Now open a connection and run InitSpatialMetadata once
    with connectable.connect() as conn:
        conn.execute(text("SELECT InitSpatialMetadata(1)"))
        # 3) Configure Alembic and run migrations
        context.configure(
            connection=conn,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
