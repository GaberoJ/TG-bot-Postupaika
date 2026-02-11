-- migration: 009_create_ed_forms_programs
-- description: Создаем таблицу связи между программами и формами обучения

-- Вверх
CREATE TABLE ed_forms_programs (
    program_id INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    education_form_id INTEGER NOT NULL REFERENCES education_forms(id) ON DELETE CASCADE,
    UNIQUE (program_id, education_form_id)
);

-- Вниз
-- DROP TABLE IF EXISTS ed_forms_programs;