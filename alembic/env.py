from logging.config import fileConfig
import os
import sys
from urllib.parse import quote_plus
from sqlalchemy.engine import URL

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 手动加载 env 文件，确保使用正确的编码
env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "env")
if os.path.exists(env_file_path):
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value and key not in os.environ:
                        os.environ[key] = value
    except UnicodeDecodeError:
        try:
            with open(env_file_path, 'r', encoding='gbk') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value and key not in os.environ:
                            os.environ[key] = value
        except Exception:
            pass

# 导入模型和配置
from app.models.base import Base
from app.models import *  # 导入所有模型
from app.config.settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 设置数据库URL（使用 SQLAlchemy URL 对象避免编码问题）
try:
    if settings.database_type.lower() == "postgresql":
        sync_url = URL.create(
            drivername="postgresql",
            username=str(settings.postgresql_user),
            password=str(settings.postgresql_password),
            host=str(settings.postgresql_host),
            port=int(settings.postgresql_port),
            database=str(settings.db_name)
        )
    elif settings.database_type.lower() == "mysql":
        sync_url = URL.create(
            drivername="mysql",
            username=str(settings.mysql_user),
            password=str(settings.mysql_password),
            host=str(settings.mysql_host),
            port=int(settings.mysql_port),
            database=str(settings.db_name)
        )
    else:
        sync_url = "sqlite:///./koalawiki.db"
    config.set_main_option("sqlalchemy.url", str(sync_url))
except Exception as e:
    import logging
    logging.error(f"构建数据库URL失败: {e}")
    raise

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
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
    if settings.database_type.lower() == "postgresql":
        # 对于 PostgreSQL，使用 creator 函数直接创建连接，避免 URL 编码问题
        user = os.getenv("POSTGRESQL_USER", str(settings.postgresql_user))
        password = os.getenv("POSTGRESQL_PASSWORD", str(settings.postgresql_password))
        host = os.getenv("POSTGRESQL_HOST", str(settings.postgresql_host))
        port = int(os.getenv("POSTGRESQL_PORT", str(settings.postgresql_port)))
        db_name = os.getenv("DB_NAME", str(settings.db_name))
        
        import psycopg2

        def connect():
            # Windows 下 psycopg2 可能与 libpq 通信时出现 UTF-8 解码错误，若此处报错可改用离线 SQL 方式迁移
            connect_host = "127.0.0.1" if str(host).lower() in ["localhost", "127.0.0.1"] else str(host)
            dsn_dict = {
                "host": connect_host,
                "port": port,
                "database": str(db_name),
                "user": str(user),
                "password": str(password),
                "client_encoding": "UTF8",
            }
            return psycopg2.connect(**dsn_dict)
        
        connectable = create_engine(
            "postgresql://",
            poolclass=pool.NullPool,
            creator=connect
        )
    else:
        # 对于其他数据库类型，使用已经构建好的 URL
        url_str = config.get_main_option("sqlalchemy.url")
        connectable = create_engine(url_str, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
