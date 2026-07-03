#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "
import psycopg2, os
psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'db'),
    port=os.getenv('POSTGRES_PORT', '5432'),
    database=os.getenv('POSTGRES_DB', 'project_db'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD', '123')
)
" 2>/dev/null; do
    echo "  PostgreSQL is not ready yet, waiting 2s..."
    sleep 2
done
echo "PostgreSQL is ready!"

echo "Applying migrations..."
python migrations/apply_migrations.py

echo "Starting bot..."
cd bot
exec python bot.py
