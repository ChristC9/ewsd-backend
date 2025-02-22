
from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context
from app.config import settings
from app.models.base import Base, CommonBase
from app.models.user_model import *
from app.models.roles_model import *
from app.models.department_model import *
from app.models.security import *
from app.models.idea_model import *
from app.models.comment_model import *
from app.models.like_model import *
from app.models.file_model import *


# Interpret the config file for Python logging.
config = context.config
fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = CommonBase.metadata

def get_db_url():
    url = settings.db_url
    return url


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
 

    context.configure(
        url=get_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        version_table='alembic',                # Specify the table name
        # version_table_schema='public'           # Specify the schema name
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        get_db_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())