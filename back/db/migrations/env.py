import os
from logging.config import fileConfig
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

from alembic import context
from db import models
from db.base import Base

load_dotenv(override=True)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importing db.models registers all ORM tables on Base.metadata for autogenerate.
assert models.User.__tablename__ == "users"
target_metadata = Base.metadata


def get_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return url


def include_object(
    object: Any,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """Limit autogenerate to ORM tables only.

    LlamaIndex PGVectorStore creates tables such as data_knowforge_vectors*
    outside Base.metadata; without this filter, autogenerate proposes dropping them.
    """
    if type_ == "table" and name not in target_metadata.tables:
        return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(get_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
