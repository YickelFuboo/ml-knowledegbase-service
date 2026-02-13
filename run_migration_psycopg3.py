"""使用 psycopg3 执行迁移 SQL，绕过 psycopg2 在 Windows 下的编码问题。"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

def main():
    from app.config.settings import settings
    if settings.database_type.lower() != "postgresql":
        print("当前仅支持 PostgreSQL")
        return 1
    host = os.getenv("POSTGRESQL_HOST", str(settings.postgresql_host))
    if host.lower() == "localhost":
        host = "127.0.0.1"
    port = int(os.getenv("POSTGRESQL_PORT", str(settings.postgresql_port)))
    user = os.getenv("POSTGRESQL_USER", str(settings.postgresql_user))
    password = os.getenv("POSTGRESQL_PASSWORD", str(settings.postgresql_password))
    dbname = os.getenv("DB_NAME", str(settings.db_name))
    sql_path = os.path.join(os.path.dirname(__file__), "migration_utf8.sql")
    if not os.path.exists(sql_path):
        print(f"未找到 {sql_path}，请先运行: poetry run alembic upgrade head --sql 并保存为 migration_utf8.sql")
        return 1
    import psycopg
    conninfo = f"host={host} port={port} user={user} password={password}"
    print("正在连接 PostgreSQL...")
    with psycopg.connect(conninfo + " dbname=postgres") as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            if cur.fetchone() is None:
                print(f"创建数据库: {dbname}")
                cur.execute(f'CREATE DATABASE "{dbname}"')
    conninfo_db = conninfo + f" dbname={dbname}"
    print("正在执行迁移 SQL...")
    with open(sql_path, "r", encoding="utf-8-sig") as f:
        sql = f.read().replace("\r\n", "\n").replace("\r", "\n")
    lines = [
        line for line in sql.split("\n")
        if not line.strip().startswith("--") and "INFO" not in line and "COMMENT ON COLUMN" not in line
    ]
    sql_clean = "\n".join(lines)
    with psycopg.connect(conninfo_db) as conn:
        conn.autocommit = False
        try:
            with conn.cursor() as cur:
                cur.execute(sql_clean)
            conn.commit()
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                conn.rollback()
                print("(表或对象已存在，迁移可能已完成)")
                return 0
            print("执行失败:", e)
            conn.rollback()
            return 1
    print("数据库迁移完成。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
