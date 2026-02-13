import os
import sys
sys.path.append(os.path.dirname(__file__))

from app.config.settings import settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migration():
    """直接执行迁移 SQL"""
    if settings.database_type.lower() != "postgresql":
        print("当前仅支持 PostgreSQL 数据库")
        return
    
    user = os.getenv("POSTGRESQL_USER", str(settings.postgresql_user))
    password = os.getenv("POSTGRESQL_PASSWORD", str(settings.postgresql_password))
    host = os.getenv("POSTGRESQL_HOST", str(settings.postgresql_host))
    port = int(os.getenv("POSTGRESQL_PORT", str(settings.postgresql_port)))
    db_name = os.getenv("DB_NAME", str(settings.db_name))
    
    # 读取 SQL 文件
    sql_file = os.path.join(os.path.dirname(__file__), "migration.sql")
    if not os.path.exists(sql_file):
        print(f"SQL 文件不存在: {sql_file}")
        print("请先运行: poetry run alembic upgrade head --sql > migration.sql")
        return
    
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password,
            client_encoding='UTF8'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # 读取并执行 SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行 SQL（按分号分割）
        for statement in sql_content.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"执行成功: {statement[:50]}...")
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"已存在，跳过: {statement[:50]}...")
                    else:
                        print(f"执行失败: {e}")
                        print(f"SQL: {statement[:100]}...")
        
        cursor.close()
        conn.close()
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_migration()
