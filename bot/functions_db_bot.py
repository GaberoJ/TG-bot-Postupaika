from typing import Dict, Any
from work_with_db import DatabaseManager
import psycopg2
from psycopg2.extras import DictCursor


class DatabaseBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.conn = self.db_manager.conn

    def get_universities_by_direction(self, direction_name: str):
        cursor = self.conn.cursor(cursor_factory=DictCursor)
        try:
            query = """
            SELECT DISTINCT
                v.id as vuz_id,
                v.name as vuz_name,
                v.city
            FROM vuzi v
            JOIN programs p ON v.id = p.vuz_id
            JOIN directions d ON p.direction_id = d.id
            WHERE d.name_dir = %s
            ORDER BY v.city, v.name
            """
            cursor.execute(query, (direction_name,))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Ошибка: {e}")
            return []
        finally:
            cursor.close()

    def get_programs_by_university_and_direction(self, vuz_id: int, direction_name: str):
        cursor = self.conn.cursor(cursor_factory=DictCursor)
        try:
            query = """
            SELECT 
                p.id,
                p.vuz_id,
                p.direction_id,
                v.name as vuz_name,
                d.name_dir as direction_name,
                p.name as program_name
            FROM programs p
            JOIN vuzi v ON p.vuz_id = v.id
            JOIN directions d ON p.direction_id = d.id
            WHERE p.vuz_id = %s AND d.name_dir = %s
            ORDER BY p.id
            """
            cursor.execute(query, (vuz_id, direction_name))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Ошибка получения программ: {e}")
            return []
        finally:
            cursor.close()

    def get_program_details(self, program_id: int):
        cursor = self.conn.cursor(cursor_factory=DictCursor)
        try:
            query = """
            SELECT 
                p.id as program_id,
                p.vuz_id,
                p.direction_id,
                v.name as vuz_name,
                v.city,
                v.link_po as vuz_link,
                d.name_dir as direction_name,
                d.num_dir as direction_code,
                p.name as program_name,
                p.education_lvl,
                p.has_budget,
                p.has_contract,
                p.count_budget,
                p.count_contract,
                p.education_cost_from,
                p.short_description,
                p.link_po as program_link,
                e.passing_grade,
                e.average_passing_grade,
                e.num_of_exams,
                e.latest_year,
                ef.education_form_id,
                f.name as education_form_name
            FROM programs p
            JOIN vuzi v ON p.vuz_id = v.id
            JOIN directions d ON p.direction_id = d.id
            LEFT JOIN entrance e ON p.id = e.program_id
            LEFT JOIN ed_forms_programs ef ON p.id = ef.program_id
            LEFT JOIN education_forms f ON ef.education_form_id = f.id
            WHERE p.id = %s
            ORDER BY ef.education_form_id
            """
            cursor.execute(query, (program_id,))
            results = cursor.fetchall()

            if not results:
                return None

            program = dict(results[0])
            education_forms = []
            for row in results:
                form_name = row.get('education_form_name')
                if form_name and form_name not in education_forms:
                    if form_name == 'full':
                        education_forms.append('Очная')
                    elif form_name == 'part':
                        education_forms.append('Очно-заочная')
                    elif form_name == 'extramural':
                        education_forms.append('Заочная')
                    else:
                        education_forms.append(form_name)

            program['education_forms'] = education_forms
            return program

        except Exception as e:
            print(f"Ошибка получения деталей программы: {e}")
            return None
        finally:
            cursor.close()

    def format_program_full(self, program_data: Dict[str, Any]) -> str:
        program_name = program_data.get('program_name', program_data['direction_name'])
        text = f"🎓 {program_name}\n\n"

        text += f"🏫 Вуз: {program_data['vuz_name']}\n"
        text += f"📍 Город: {program_data['city']}\n"
        text += f"📋 Направление: {program_data['direction_name']}\n"

        if program_data.get('direction_code'):
            text += f"🔢 Код направления: {program_data['direction_code']}\n"

        lvl = program_data.get('education_lvl', '')
        if lvl == 'bak':
            text += "📚 Уровень: Бакалавриат\n"
        elif lvl == 'mag':
            text += "📚 Уровень: Магистратура\n"
        elif lvl == 'spec':
            text += "📚 Уровень: Специалитет\n"
        elif lvl:
            text += f"📚 Уровень: {lvl}\n"

        if program_data.get('education_forms'):
            forms = ', '.join(program_data['education_forms'])
            text += f"📝 Формы обучения: {forms}\n"

        text += "\n"

        if program_data.get('has_budget'):
            budget_count = program_data.get('count_budget', 'н/д')
            if budget_count and budget_count != 'н/д':
                text += f"✅ Бюджетные места: {budget_count}\n"
            else:
                text += "✅ Бюджетные места: есть\n"
        else:
            text += "❌ Бюджетные места: нет\n"

        if program_data.get('has_contract'):
            contract_count = program_data.get('count_contract', 'н/д')
            cost = program_data.get('education_cost_from')
            if cost and cost > 0:
                text += f"💰 Контрактные места: {contract_count} от {cost:,} ₽/год\n".replace(',', ' ')
            elif contract_count and contract_count != 'н/д':
                text += f"💰 Контрактные места: {contract_count}\n"
            else:
                text += "💰 Контрактные места: есть\n"
        else:
            text += "❌ Контрактные места: нет\n"

        text += "\n"

        if program_data.get('passing_grade') and program_data['passing_grade'] > 0:
            text += f"📊 Проходной балл: {program_data['passing_grade']}\n"
        if program_data.get('average_passing_grade') and program_data['average_passing_grade'] > 0:
            text += f"📈 Средний балл: {program_data['average_passing_grade']}\n"
        if program_data.get('num_of_exams') and program_data['num_of_exams'] > 0:
            text += f"📝 Количество экзаменов: {program_data['num_of_exams']}\n"
        if program_data.get('latest_year'):
            text += f"📅 Данные за: {program_data['latest_year']} г.\n"

        text += "\n"

        if program_data.get('short_description'):
            text += f"📄 Описание:\n{program_data['short_description']}\n\n"
        if program_data.get('program_link'):
            text += f"🔗 Программа: {program_data['program_link']}\n"
        if program_data.get('vuz_link'):
            text += f"🏛 Сайт вуза: {program_data['vuz_link']}\n"

        return text

    def close(self):
        self.db_manager.close()