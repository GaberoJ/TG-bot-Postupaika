-- migration: 003_add_vuz_id_to_programs
-- description: Добавляем колонку vuz_id в таблицу programs

-- Вверх
ALTER TABLE programs ADD COLUMN vuz_id INTEGER;

ALTER TABLE programs
ADD CONSTRAINT fk_programs_vuzi
FOREIGN KEY (vuz_id) REFERENCES vuzi(id) ON DELETE CASCADE;

-- Вниз
-- ALTER TABLE programs DROP CONSTRAINT IF EXISTS fk_programs_vuzi;
-- ALTER TABLE programs DROP COLUMN IF EXISTS vuz_id;