import os
import psycopg2


def apply_migrations():
    """Применяет все миграции из папки migrations/"""

    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'project_db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', '123')
    )
    cur = conn.cursor()

    print("=" * 50)
    print("ПРИМЕНЕНИЕ МИГРАЦИЙ БАЗЫ ДАННЫХ")
    print("=" * 50)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    cur.execute("SELECT migration_name FROM _migrations")
    applied = {row[0] for row in cur.fetchall()}

    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    migration_files = sorted([
        f for f in os.listdir(migrations_dir)
        if f.endswith('.sql')
    ])

    print(f"Найдено файлов миграций: {len(migration_files)}")

    for migration_file in migration_files:
        if migration_file in applied:
            print(f"✓ Уже применена: {migration_file}")
            continue

        print(f"Применяю: {migration_file}")

        with open(os.path.join(migrations_dir, migration_file), 'r', encoding='utf-8') as f:
            content = f.read()

        if '-- Вниз' in content:
            sql = content.split('-- Вниз')[0].replace('-- Вверх', '').strip()
        else:
            sql = content.strip()

        try:
            cur.execute(sql)

            cur.execute(
                "INSERT INTO _migrations (migration_name) VALUES (%s)",
                (migration_file,)
            )

            conn.commit()
            print(f"  ✅ Успешно применена")

        except Exception as e:
            conn.rollback()
            print(f"  ❌ Ошибка: {e}")
            print(f"  SQL: {sql[:100]}...")
            break

    cur.close()
    conn.close()
    print("\n" + "=" * 50)
    print("ГОТОВО!")
    print("=" * 50)


if __name__ == "__main__":
    apply_migrations()
