-- migration: 006_add_unique_to_num_dir
-- description: Добавляем уникальное ограничение на колонку num_dir

-- Вверх
ALTER TABLE directions ADD CONSTRAINT directions_num_dir_unique UNIQUE (num_dir);

-- Вниз
-- ALTER TABLE directions DROP CONSTRAINT IF EXISTS directions_num_dir_unique;