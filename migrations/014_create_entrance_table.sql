-- migration: 014_create_entrance_table
-- description: Удаляем старые поля из programs и создаем таблицу entrance

-- Вверх
-- 1. Удаляем старые поля из таблицы programs
ALTER TABLE programs
DROP COLUMN IF EXISTS passing_grade,
DROP COLUMN IF EXISTS average_passing_grade,
DROP COLUMN IF EXISTS num_of_exams,
DROP COLUMN IF EXISTS latest_year;

-- 2. Создаем таблицу entrance
CREATE TABLE IF NOT EXISTS entrance (
    id SERIAL PRIMARY KEY,
    program_id INTEGER NOT NULL,
    type VARCHAR(10) CHECK (type IN ('budget', 'contract')), -- 'budget' или 'contract'
    passing_grade INTEGER,
    average_passing_grade INTEGER,
    num_of_exams INTEGER,
    latest_year INTEGER,
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE,
    UNIQUE (program_id, type) -- одна запись каждого типа на программу
);

-- Вниз
-- ALTER TABLE programs
-- ADD COLUMN IF NOT EXISTS passing_grade INTEGER,
-- ADD COLUMN IF NOT EXISTS average_passing_grade INTEGER,
-- ADD COLUMN IF NOT EXISTS num_of_exams INTEGER,
-- ADD COLUMN IF NOT EXISTS latest_year INTEGER;
--
-- DROP TABLE IF EXISTS entrance;