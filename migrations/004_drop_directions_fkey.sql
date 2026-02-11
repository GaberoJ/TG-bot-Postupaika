-- migration: 004_drop_directions_fkey
-- description: Удаляем старый внешний ключ directions_vuz_id_fkey

-- Вверх
ALTER TABLE directions
DROP CONSTRAINT IF EXISTS directions_vuz_id_fkey;

-- Вниз
-- ALTER TABLE directions
-- ADD CONSTRAINT directions_vuz_id_fkey
-- FOREIGN KEY (vuz_id) REFERENCES vuzi(id) ON DELETE CASCADE;