-- migration: 007_add_short_description_to_programs
-- description: Добавляем колонку short_description в таблицу programs

-- Вверх
ALTER TABLE programs ADD COLUMN short_description TEXT;

-- Вниз
-- ALTER TABLE programs DROP COLUMN IF EXISTS short_description;