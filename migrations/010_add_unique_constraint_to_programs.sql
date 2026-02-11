-- migration: 010_add_unique_constraint_to_programs
-- description: Добавляем UNIQUE constraint для link_po в таблице programs

-- Вверх
ALTER TABLE programs ADD CONSTRAINT programs_link_po_unique UNIQUE (link_po);

-- Вниз
-- ALTER TABLE programs DROP CONSTRAINT IF EXISTS programs_link_po_unique;