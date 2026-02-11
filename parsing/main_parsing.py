from work_with_db import DatabaseManager
from parse_vuzi import *
from parse_directions import parse_all_directions
from parse_programs_outside import parse_programs_from_url
from parse_programs_inside import parse_program_details
import threading
from queue import Queue
import time

def vuzi_parse_and_add_in_db():
    db = DatabaseManager()
    db.close()

    base_url = "https://postupi.online/vuzi/"
    lst_of_vuzes = []

    page_urls = pagination(base_url,
                           max_pages=65)

    for i, page_url in enumerate(page_urls, 1):
        page_vuzi = parse_vuzi_from_page(page_url)
        lst_of_vuzes.extend(page_vuzi)
        time.sleep(0.4)

    for i, vuz in enumerate(lst_of_vuzes, 1):
        success = get_city_for_vuz(vuz)
        if i % 10 == 0:
            print(f"Обработано городов для вузов: {i} / {len(lst_of_vuzes)}")
            time.sleep(0.4)

    db = DatabaseManager()
    for vuz in lst_of_vuzes:
        cur_vuz_data = {
            "name": vuz.name,
            "city": vuz.city,
            "link_po": vuz.link
        }
        db.insert_data("vuzi", cur_vuz_data)

    print("Данные успешно добавлены в БД")

    db.close()

def directions_and_add_in_db():
    from work_with_db import DatabaseManager

    directions = parse_all_directions()

    db = DatabaseManager()
    cur = db.conn.cursor()

    added = 0
    for d in directions:
        try:
            cur.execute("""
                INSERT INTO directions (num_dir, name_dir, link_dir) 
                VALUES (%s, %s, %s)
                ON CONFLICT (num_dir) DO NOTHING
            """, (d['num_dir'], d['name_dir'], d['link_dir']))

            if cur.rowcount > 0:
                added += 1

        except Exception as e:
            print(f"Ошибка: {d['num_dir']} - {e}")

    db.conn.commit()
    print(f"✅ Добавлено новых направлений: {added}")
    print(f"   Всего в БД: {len(directions)}")

    cur.close()
    db.close()

def programs_parse_and_add_in_db_outside():
    from work_with_db import DatabaseManager

    db = DatabaseManager()

    cur = db.conn.cursor()
    cur.execute("SELECT id, link_po FROM vuzi")
    vuzi_list = cur.fetchall()
    cur.close()

    print(f"📊 Найдено {len(vuzi_list)} вузов в БД")

    total_programs = 0

    for vuz_id, vuz_link in vuzi_list:
        try:
            if vuz_link.endswith('/'):
                vuz_link = vuz_link[:-1]

            programs_url = f"{vuz_link}/programmy-obucheniya/bakalavr/"

            print(f"\n🔍 Парсим программы вуза ID {vuz_id}:")
            print(f"   URL: {programs_url}")

            programs = parse_programs_from_url(programs_url)

            if not programs:
                print(f"   ⚠️  Программы не найдены")
                time.sleep(1)
                continue

            cur = db.conn.cursor()
            added_count = 0

            for program in programs:
                try:
                    direction_id = None
                    if program['num_dir']:
                        cur.execute("SELECT id FROM directions WHERE num_dir = %s", (program['num_dir'],))
                        result = cur.fetchone()
                        if result:
                            direction_id = result[0]

                    program_data = {
                        'direction_id': direction_id,
                        'has_budget': program['has_budget'],
                        'has_contract': program['has_contract'],
                        'count_budget': program['count_budget'],
                        'count_contract': program['count_contract'],
                        'education_cost_from': program['education_cost_from'],
                        'link_po': program['link_po'],
                        'vuz_id': vuz_id
                    }

                    cur.execute("""
                        INSERT INTO programs 
                        (direction_id, has_budget, has_contract, count_budget, count_contract, 
                         education_cost_from, link_po, vuz_id)
                        VALUES (%(direction_id)s, %(has_budget)s, %(has_contract)s, %(count_budget)s, 
                                %(count_contract)s, %(education_cost_from)s, %(link_po)s, %(vuz_id)s)
                        ON CONFLICT (link_po) DO NOTHING
                    """, program_data)

                    if cur.rowcount > 0:
                        added_count += 1

                except Exception as e:
                    print(f"    ✗ Ошибка при добавлении программы: {e}")
                    continue

            db.conn.commit()
            cur.close()

            total_programs += len(programs)
            print(f"   ✅ Добавлено/обновлено программ: {added_count} из {len(programs)}")

            time.sleep(1)

        except Exception as e:
            print(f"   ✗ Ошибка при обработке вуза {vuz_id}: {e}")
            continue

    db.close()

    print(f"\n{'=' * 60}")
    print(f"✅ ВСЕГО ОБРАБОТАНО ПРОГРАММ: {total_programs}")
    print(f"{'=' * 60}")

def programs_parse_and_add_in_db_inside():
    db = DatabaseManager()

    cur = db.conn.cursor()
    cur.execute("""
        SELECT id, link_po FROM programs 
        WHERE name IS NULL 
        ORDER BY id 
    """)
    programs_to_update = cur.fetchall()
    cur.close()

    print(f"📊 Найдено {len(programs_to_update)} программ для обновления")

    if not programs_to_update:
        print("⚠️  Все программы уже обновлены")
        db.close()
        return

    queue = Queue()
    for program in programs_to_update:
        queue.put(program)

    results_lock = threading.Lock()
    results = {
        'total': len(programs_to_update),
        'updated': 0,
        'errors': 0
    }

    def worker(worker_id):
        local_db = DatabaseManager()

        while True:
            try:
                program_id, program_link = queue.get_nowait()
            except:
                break

            try:
                with results_lock:
                    print(f"\n🔄 Обновляем программу ID {program_id} (поток {worker_id}):")

                program_details = parse_program_details(program_link)

                if program_details['name']:
                    cur = local_db.conn.cursor()

                    update_data = {
                        'name': program_details['name'],
                        'education_lvl': program_details['education_lvl'],
                        'short_description': program_details['short_description'],
                        'program_id': program_id
                    }

                    cur.execute("""
                        UPDATE programs 
                        SET name = %(name)s,
                            education_lvl = %(education_lvl)s,
                            short_description = %(short_description)s
                        WHERE id = %(program_id)s
                    """, update_data)

                    education_forms = program_details['education_form']

                    if education_forms:
                        for form_name in education_forms:
                            cur.execute("SELECT id FROM education_forms WHERE name = %s", (form_name,))
                            result = cur.fetchone()

                            if result:
                                form_id = result[0]
                                try:
                                    cur.execute("""
                                        INSERT INTO ed_forms_programs (program_id, education_form_id)
                                        VALUES (%s, %s)
                                        ON CONFLICT (program_id, education_form_id) DO NOTHING
                                    """, (program_id, form_id))
                                except Exception as e:
                                    with results_lock:
                                        print(f"   ⚠️  Ошибка при добавлении формы {form_name}: {e}")
                            else:
                                with results_lock:
                                    print(f"   ⚠️  Форма обучения '{form_name}' не найдена в таблице education_form")

                    local_db.conn.commit()
                    cur.close()

                    with results_lock:
                        results['updated'] += 1

                else:
                    with results_lock:
                        results['errors'] += 1
                        print(f"   ⚠️  Не удалось получить детали программы")

                with results_lock:
                    processed = results['updated'] + results['errors']
                    if processed % 100 == 0:
                        print(f"\n📊 Прогресс: {processed}/{results['total']} "
                              f"(✓ {results['updated']}, ✗ {results['errors']})")

            except Exception as e:
                with results_lock:
                    results['errors'] += 1
                    print(f"   ✗ Ошибка при обновлении программы {program_id}: {e}")

            finally:
                queue.task_done()

        local_db.close()

    num_threads = 20
    threads = []

    print(f"\n🚀 Запускаем {num_threads} потоков для обработки...")

    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i + 1,), daemon=True)
        t.start()
        threads.append(t)

    queue.join()

    for t in threads:
        t.join(timeout=1)

    print(f"\n{'=' * 60}")
    print(f"📊 ИТОГИ (многопоточность):")
    print(f"   Всего обработано: {results['total']}")
    print(f"   Успешно обновлено: {results['updated']}")
    print(f"   С ошибками: {results['errors']}")
    print(f"{'=' * 60}")

def entrance_parse_and_add_in_db():
    from work_with_db import DatabaseManager
    from parsing.parse_entrance import parse_passing_grades
    import threading
    from queue import Queue

    db = DatabaseManager()

    cur = db.conn.cursor()
    cur.execute("""
        SELECT p.id, p.link_po 
        FROM programs p 
        ORDER BY p.id 
    """)
    programs_to_update = cur.fetchall()
    cur.close()

    print(f"📊 Найдено {len(programs_to_update)} программ для обновления проходных баллов")

    if not programs_to_update:
        print("⚠️  Все программы уже обновлены")
        db.close()
        return

    queue = Queue()
    for program in programs_to_update:
        queue.put(program)

    results_lock = threading.Lock()
    results = {
        'total': len(programs_to_update),
        'updated_budget': 0,
        'updated_contract': 0,
        'errors': 0
    }

    def worker(worker_id):
        local_db = DatabaseManager()

        while True:
            try:
                program_id, program_link = queue.get_nowait()
            except:
                break

            try:
                with results_lock:
                    processed = results['updated_budget'] + results['updated_contract'] + results['errors']
                    if processed % 20 == 0:
                        print(f"🔄 ID {program_id} (поток {worker_id})")

                grades = parse_passing_grades(program_link)

                if grades['budget']['passing_grade'] is not None:
                    cur = local_db.conn.cursor()
                    cur.execute("""
                        INSERT INTO entrance 
                        (program_id, type, passing_grade, average_passing_grade, num_of_exams, latest_year)
                        VALUES (%s, 'budget', %s, %s, %s, %s)
                        ON CONFLICT (program_id, type) DO NOTHING
                    """, (program_id,
                          grades['budget']['passing_grade'],
                          grades['budget']['average_passing_grade'],
                          grades['budget']['num_of_exams'],
                          grades['budget']['latest_year']))
                    local_db.conn.commit()
                    cur.close()

                    with results_lock:
                        results['updated_budget'] += 1

                if grades['contract']['passing_grade'] is not None:
                    cur = local_db.conn.cursor()
                    cur.execute("""
                        INSERT INTO entrance 
                        (program_id, type, passing_grade, average_passing_grade, num_of_exams, latest_year)
                        VALUES (%s, 'contract', %s, %s, %s, %s)
                        ON CONFLICT (program_id, type) DO UPDATE SET
                            passing_grade = EXCLUDED.passing_grade,
                            average_passing_grade = EXCLUDED.average_passing_grade,
                            num_of_exams = EXCLUDED.num_of_exams,
                            latest_year = EXCLUDED.latest_year
                    """, (program_id,
                          grades['contract']['passing_grade'],
                          grades['contract']['average_passing_grade'],
                          grades['contract']['num_of_exams'],
                          grades['contract']['latest_year']))
                    local_db.conn.commit()
                    cur.close()

                    with results_lock:
                        results['updated_contract'] += 1

                with results_lock:
                    processed = results['updated_budget'] + results['updated_contract'] + results['errors']
                    if processed % 50 == 0:
                        print(
                            f"📊 Прогресс: {processed}/{results['total']} (бюджет: {results['updated_budget']}, контракт: {results['updated_contract']}, ошибки: {results['errors']})")

            except Exception as e:
                with results_lock:
                    results['errors'] += 1
                    if results['errors'] % 10 == 0:
                        print(f"✗ Ошибка программы {program_id}: {e}")

            finally:
                queue.task_done()

        local_db.close()

    num_threads = 10
    threads = []

    print(f"🚀 Запускаем {num_threads} потоков...")

    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i + 1,), daemon=True)
        t.start()
        threads.append(t)

    queue.join()

    for t in threads:
        t.join(timeout=1)

    print(f"\n{'=' * 60}")
    print(f"📊 ИТОГИ:")
    print(f"   Всего программ: {results['total']}")
    print(f"   Обновлено бюджетных записей: {results['updated_budget']}")
    print(f"   Обновлено платных записей: {results['updated_contract']}")
    print(f"   Ошибки: {results['errors']}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    """Полный парсинг вообще всего и запись в БД"""
    # vuzi_parse_and_add_in_db()
    # directions_and_add_in_db()
    # programs_parse_and_add_in_db_outside()
    # programs_parse_and_add_in_db_inside()
    # entrance_parse_and_add_in_db()