-- migration: 012_drop_education_form_column
-- description: Удаляем колонку education_form из таблицы programs

-- Вверх
ALTER TABLE programs DROP COLUMN IF EXISTS education_form;

-- Вниз
-- ALTER TABLE programs ADD COLUMN education_form VARCHAR(50);