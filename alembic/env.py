from logging.config import fileConfig
from dotenv import load_dotenv
import os
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from app.models import User, Transaction
from app.models.base import db

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
database_url = os.getenv("DATABASE_URL")
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = db
config.set_main_option("sqlalchemy.url", database_url)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
