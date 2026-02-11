import requests
from bs4 import BeautifulSoup
import time


def parse_all_directions_general(base_url):
    """Парсит все направления из общего списка (бакалавриат/специалитет)"""

    session = requests.Session()
    # Ваши cookies
    session.cookies.update({
        '_ym_uid': '1761810989641643334',
        '_ym_d': '1761810989',
        'city_id': '-1',
        'guid': 'c6f6784a-ae86-4f0d-bcaf-37d1a7eabaf1',
        'uid': 'x%9C3473%B404%B0%B4%B0%00%00%0BB%02%12',
        'sticker_val': '2334',
        'sticker_val_1': '1',
        'popup-asterisk': '1',
        'rmass': '13%2C115%2C183',
        'r_fresh_70': '2',
        '_ym_isad': '2',
        '_ym_visorc': 'w',
        'popup-setup': '1',
        'sid_group': '0a35d3d1-2b8b-4d44-b7c9-fdeaa9794477',
        'sid_group_gen': '0',
        'user_reg': '6213133%7EBCCF22D4AD0996A2',
        'pi': '%11%03%1F%5BVSJ%3E%01%0DH%19%110%0C%17%18%1D%02%0AY%1A%12%1C%3C%05%04%09%00%1A%3ED%07%18%1B%0E%1F%15%03%02F%7CNB%06%05%0Fp%1B%17%16%17%1D%12%19%18%11FhBBDJ%023%07JHEW%5CK%14%13%1D6%02%0FZXSoHFZ%11%03%1F%5B%05%02%068%1F%00%0A%04%02p%5CJ%09%02%00%14Y%10%08%082%1ENDJ%40%3E%07%09V%00%1D%1C%13%07%11%042%0CNPF%07%3A%12%04%0D_LPW%14%1C%05p%1D%13%08%0E%11%3E%06%08%18_X%5C%02%14%02%00%3E%03%15%0EF%40%7CH%04%15%1C%40BAM_V1%18%0CZ_%40%7CH%04%15%1C%40%07%11%06%04F4%0C%0D%0C%1C%0F%3E%1F%0A%0B%5D%0A%14%11ZO%19-%02%07%0E%05%06%00%02%01DG',
        'sid_track': '012%2C158%2C012%2C012%2C008%2C000',
        'current-page': '000',
        'sid_group_time': '1762112491999'
    })
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    all_directions = []
    page = 1

    print(f"🔍 Парсим общий список направлений: {base_url}")

    while True:
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page_num={page}"

        print(f"  Страница {page}...")

        try:
            response = session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Проверяем редирект
            if 'page_num' in url and 'page_num' not in response.url:
                print(f"    Редирект, страниц больше нет")
                break

            # Ищем все блоки с направлениями
            # Новый формат: код и короткое название в <a> тегах внутри <p class="list__pre">
            direction_blocks = soup.find_all('p', class_='list__pre')
            page_directions = []

            for block in direction_blocks:
                try:
                    # Ищем первый <a> внутри первого <span> - это код и ссылка
                    first_span = block.find('span')
                    if not first_span:
                        continue

                    a_tag = first_span.find('a')
                    if not a_tag:
                        continue

                    # Код направления и ссылка
                    num_dir = a_tag.text.strip()
                    link_dir = a_tag['href']
                    if link_dir.startswith('/'):
                        link_dir = f"https://postupi.online{link_dir}"

                    # Полное название направления из h2.list__h
                    # Ищем следующий h2 после блока
                    h2_tag = block.find_next('h2', class_='list__h')
                    name_dir = None
                    if h2_tag:
                        name_dir_a = h2_tag.find('a')
                        if name_dir_a:
                            name_dir = name_dir_a.text.strip()

                    # Если не нашли в h2, берем из второго span
                    if not name_dir:
                        second_span = block.find_all('span')
                        if len(second_span) >= 2:
                            name_dir = second_span[1].text.strip()

                    if num_dir and name_dir and link_dir:
                        page_directions.append({
                            'num_dir': num_dir,
                            'name_dir': name_dir,
                            'link_dir': link_dir
                        })

                except Exception as e:
                    continue  # Пропускаем ошибки в отдельных блоках

            print(f"    Найдено: {len(page_directions)} направлений")

            # Если страница пустая и это не первая страница - заканчиваем
            if not page_directions and page > 1:
                print("    Страница пустая, заканчиваем")
                break

            all_directions.extend(page_directions)

            # Проверяем, есть ли еще страницы
            if len(page_directions) < 20:
                next_url = f"{base_url}?page_num={page + 1}"
                try:
                    test_resp = session.head(next_url, timeout=5, allow_redirects=False)
                    if test_resp.status_num_dir != 200:
                        break
                except:
                    break

            time.sleep(0.5)
            page += 1

        except Exception as e:
            print(f"    Ошибка: {e}")
            break

    print(f"✅ Всего направлений собрано: {len(all_directions)}")
    return all_directions


def parse_all_bachelor_directions():
    """Парсит все направления бакалавриата"""
    base_url = "https://postupi.online/specialnosti/bakalavr/"
    return parse_all_directions_general(base_url)


def parse_all_specialist_directions():
    """Парсит все направления специалитета"""
    base_url = "https://postupi.online/specialnosti/specialist/"
    return parse_all_directions_general(base_url)


def parse_all_directions():
    """Парсит все направления (бакалавриат + специалитет)"""
    print("=" * 60)
    print("ПАРСИНГ ОБЩЕГО СПИСКА НАПРАВЛЕНИЙ")
    print("=" * 60)

    # Парсим бакалавриат
    print("\n🎓 БАКАЛАВРИАТ:")
    bachelor = parse_all_bachelor_directions()

    # Парсим специалитет
    print("\n🎓 СПЕЦИАЛИТЕТ:")
    specialist = parse_all_specialist_directions()

    # Объединяем
    all_directions = bachelor + specialist

    print(f"\n📊 ИТОГО:")
    print(f"  Бакалавриат: {len(bachelor)} направлений")
    print(f"  Специалитет: {len(specialist)} направлений")
    print(f"  Всего: {len(all_directions)} направлений")

    return all_directions


# Использование
if __name__ == "__main__":
    # Тест парсинга
    print("=" * 60)
    print("ТЕСТ ПАРСИНГА ОБЩЕГО СПИСКА НАПРАВЛЕНИЙ")
    print("=" * 60)

    # Можно тестировать отдельно
    # directions = parse_all_bachelor_directions()
    # directions = parse_all_specialist_directions()

    # Или все вместе
    directions = parse_all_directions()

    print("\n📋 Примеры найденных направлений:")
    for i, d in enumerate(directions[:10], 1):
        print(f"{i}. [{d['num_dir']}] {d['name_dir']}")
        print(f"   🔗 {d['link_dir']}")

    if len(directions) > 10:
        print(f"... и еще {len(directions) - 10} направлений")