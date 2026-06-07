# services/core/migrations/env.py
import asyncio
import sys
from os.path import dirname, abspath
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Добавляем корневую папку приложения в sys.path, чтобы Alembic видел модуль src
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# Импортируем нашу единую декларативную базу моделей и URL базы данных
from src.models import Base
from src.database import DATABASE_URL

# Это объект конфигурации Alembic
config = context.config

# Настраиваем логирование на основе файла alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаем метаданные наших пофайловых моделей для автогенерации таблиц
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме."""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Вспомогательная функция для выполнения миграций внутри соединения."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Запуск миграций в асинхронном online режиме."""
    # Динамически подставляем URL из переменных окружения Docker в конфиг Alembic
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = DATABASE_URL

    # Создаем асинхронный движок
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
