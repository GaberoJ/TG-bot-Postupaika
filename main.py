from work_with_db import DatabaseManager
from parse_vuzi import *

if __name__ == "__main__":
    db = DatabaseManager()  # Чтобы проверить сразу, удалось ли подключиться к БД
    db.close()

    base_url = "https://postupi.online/vuzi/"
    lst_of_vuzes = []

    page_urls = pagination(base_url,
                           max_pages=2)  # Можно увеличить количество страниц (Всего 58 страниц (включая base_url))

    """Парсим Вузы и ссылки на них"""
    for i, page_url in enumerate(page_urls, 1):
        page_vuzi = parse_vuzi_from_page(page_url)
        lst_of_vuzes.extend(page_vuzi)
        time.sleep(0.5)

    """Добавляем города"""
    for i, vuz in enumerate(lst_of_vuzes, 1):
        success = get_city_for_vuz(vuz)
        if i % 10 == 0:
            print(f"Обработано городов для вузов: {i} / {len(lst_of_vuzes)}")
            time.sleep(0.5)

    """Вставляем данные в БД"""
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
