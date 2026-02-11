-- migration: 011_add_unique_to_ed_forms_programs
-- description: Добавляем UNIQUE constraint для program_id и education_form_id

-- Вверх
ALTER TABLE ed_forms_programs ADD CONSTRAINT ed_forms_programs_unique UNIQUE (program_id, education_form_id);

-- Вниз
-- ALTER TABLE ed_forms_programs DROP CONSTRAINT IF EXISTS ed_forms_programs_unique;