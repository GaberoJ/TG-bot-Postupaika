-- migration: 002_add_unique_constraint
-- description: Добавляем уникальное ограничение в таблицу directions

-- Вверх
ALTER TABLE directions
ADD CONSTRAINT directions_unique_vuz_dir
UNIQUE (num_dir, name_dir, vuz_id);

-- Вниз
-- ALTER TABLE directions DROP CONSTRAINT IF EXISTS directions_unique_vuz_dir;