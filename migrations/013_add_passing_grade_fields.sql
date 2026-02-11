-- migration: 013_add_passing_grade_fields
-- description: Добавляем поля passing_grade и average_passing_grade в таблицу programs

-- Вверх
ALTER TABLE programs
ADD COLUMN IF NOT EXISTS passing_grade INTEGER,
ADD COLUMN IF NOT EXISTS average_passing_grade INTEGER,
ADD COLUMN IF NOT EXISTS num_of_exams INTEGER,
ADD COLUMN IF NOT EXISTS latest_year INTEGER;

-- Вниз
-- ALTER TABLE programs
-- DROP COLUMN IF EXISTS passing_grade,
-- DROP COLUMN IF EXISTS average_passing_grade;