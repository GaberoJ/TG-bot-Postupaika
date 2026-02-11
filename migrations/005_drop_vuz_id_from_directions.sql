-- migration: 005_drop_vuz_id_from_directions
-- description: Удаляем колонку vuz_id из таблицы directions (теперь это связь через direction_id -> directions -> vuzi)

-- Вверх
ALTER TABLE directions DROP COLUMN IF EXISTS vuz_id;

-- Вниз
-- ALTER TABLE directions ADD COLUMN vuz_id INTEGER;
-- ALTER TABLE directions ADD CONSTRAINT directions_vuz_id_fkey
--     FOREIGN KEY (vuz_id) REFERENCES vuzi(id) ON DELETE CASCADE;