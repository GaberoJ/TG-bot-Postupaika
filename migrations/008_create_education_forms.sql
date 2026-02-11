-- migration: 008_create_education_forms
-- description: Создаем таблицу форм обучения и заполняем базовыми значениями

-- Вверх
CREATE TABLE education_forms (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Заполняем базовые формы обучения
INSERT INTO education_forms (name) VALUES
    ('очно'),
    ('заочно'),
    ('очно-заочно'),
    ('дистанционно'),
    ('выходного дня')
ON CONFLICT (name) DO NOTHING;

-- Вниз
-- DROP TABLE IF EXISTS education_forms;