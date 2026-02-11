import requests
from bs4 import BeautifulSoup
import time
import re


def parse_programs_from_url(base_url):
    """Парсит все программы обучения со страницы направления"""

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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    session.headers.update(headers)

    all_programs = []
    page = 1

    print(f"🔍 Парсим программы: {base_url}")

    while True:
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page_num={page}"

        print(f"  Страница {page}...")

        try:
            response = session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            if 'page_num' in url and 'page_num' not in response.url:
                print(f"    Редирект, страниц больше нет")
                break

            program_blocks = soup.find_all('li', class_='list')

            if not program_blocks:
                print(f"    На странице нет программ")
                break

            page_programs = []

            for block in program_blocks:
                try:

                    program_link = None
                    h2_tag = block.find('h2', class_='list__h')
                    if h2_tag:
                        a_tag = h2_tag.find('a')
                        if a_tag and 'href' in a_tag.attrs:
                            program_link = a_tag['href']

                    direction_code = None
                    list_pre_block = block.find('p', class_='list__pre')
                    if list_pre_block:
                        # Ищем ссылку с кодом (пример: specialnost/31.05.01/)
                        code_link = list_pre_block.find('a', href=re.compile(r'specialnost/\d+\.\d+\.\d+/'))
                        if code_link:
                            direction_code = code_link.text.strip()
                        else:
                            # Ищем паттерн кода в тексте блока
                            code_match = re.search(r'\d{2}\.\d{2}\.\d{2}', list_pre_block.text)
                            if code_match:
                                direction_code = code_match.group()


                    # 2. Бюджетные и платные места
                    budget_places = 0
                    contract_places = 0
                    has_budget = False
                    has_contract = False

                    score_wrap = block.find('div', class_='list__score-wrap')
                    if score_wrap:
                        score_items = score_wrap.find_all('p', class_='list__score')

                        for item in score_items:
                            full_text = item.get_text(' ', strip=True)

                            if 'бюджет' in full_text.lower():
                                b_tags = item.find_all('b')
                                if b_tags:
                                    for b_tag in b_tags:
                                        b_text = b_tag.text.strip()
                                        if b_text.lower() == 'нет':
                                            budget_places = 0
                                            has_budget = False
                                            break
                                        else:
                                            numbers = re.findall(r'\b\d+\b', b_text)
                                            if numbers:
                                                budget_places = int(numbers[0])
                                                has_budget = True
                                                break
                                else:
                                    numbers = re.findall(r'\b\d+\b', full_text)
                                    if numbers:
                                        budget_places = int(numbers[0])
                                        has_budget = True

                            elif 'платн' in full_text.lower():
                                b_tags = item.find_all('b')
                                if b_tags:
                                    for b_tag in b_tags:
                                        b_text = b_tag.text.strip()
                                        numbers = re.findall(r'\b\d+\b', b_text)
                                        if numbers:
                                            contract_places = int(numbers[-1])
                                            has_contract = True
                                            break
                                else:
                                    numbers = re.findall(r'\b\d+\b', full_text)
                                    if numbers:
                                        contract_places = int(numbers[-1])
                                        has_contract = True

                    # 3. Цена
                    price_per_year = None

                    # Способ 1: Ищем блок с ценой
                    price_blocks = block.find_all(['div', 'span'], class_=lambda x: x and (
                            'price' in str(x).lower() or 'cost' in str(x).lower()))

                    for price_block in price_blocks:
                        price_text = price_block.get_text(' ', strip=True)

                        # Ищем все числа в тексте
                        numbers = re.findall(r'[\d\s]+', price_text)
                        for num_str in numbers:
                            # Очищаем строку от пробелов
                            clean_num = num_str.replace(' ', '').replace('\xa0', '')
                            if clean_num.isdigit():
                                price_candidate = int(clean_num)
                                price_per_year = price_candidate
                                break
                        if price_per_year:
                            break


                    # Собираем данные программы
                    program_data = {
                        'num_dir': direction_code,
                        'has_budget': has_budget,
                        'has_contract': has_contract,
                        'count_budget': budget_places,
                        'count_contract': contract_places,
                        'education_cost_from': price_per_year,
                        'link_po' : program_link
                    }

                    page_programs.append(program_data)

                    # Выводим информацию для отладки
                    price_info = f"Цена: {price_per_year}" if price_per_year else "Цена: не найдена"
                    print(
                        f"      Направление: {direction_code}, Бюджет: {budget_places}, Платно: {contract_places}, {price_info}")

                except Exception as e:
                    print(f"    ✗ Ошибка в блоке программы: {e}")
                    continue

            print(f"    Найдено программ: {len(page_programs)}")

            if not page_programs:
                print("    Страница пустая, заканчиваем")
                break

            all_programs.extend(page_programs)

            # Проверка пагинации
            pagination = soup.find('div', class_='paginator')
            if pagination:
                next_link = pagination.find('a', text='›')
                if not next_link:
                    break
            elif len(page_programs) < 20:
                break

            time.sleep(1)
            page += 1

        except Exception as e:
            print(f"    Ошибка на странице {page}: {e}")
            break

    print(f"✅ Всего программ собрано: {len(all_programs)}")

    # Статистика
    codes_found = sum(1 for p in all_programs if p['num_dir'] is not None)
    prices_found = sum(1 for p in all_programs if p['education_cost_from'] is not None)
    print(f"📊 Кодов направлений найдено: {codes_found} из {len(all_programs)}")
    print(f"📊 Цен найдено: {prices_found} из {len(all_programs)}")

    return all_programs



# Пример использования
if __name__ == "__main__":
    test_url = "https://nn.postupi.online/vuz/nizhegorodskij-gosudarstvennyj-arhitekturno-stroitelnyj-universitet/programmy-obucheniya/bakalavr/"

    print("=" * 60)
    print("ПАРСИНГ ПРОГРАММ (ИСПРАВЛЕННЫЙ ПОИСК КОДА)")
    print("=" * 60)

    # Сначала дебаг
    print("\n🔍 Анализируем структуру для поиска кода направления...")

    # Затем парсим
    print("\n" + "=" * 60)
    print("НАЧИНАЕМ ПАРСИНГ")
    print("=" * 60)

    programs = parse_programs_from_url(test_url)

    print("\n📋 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 60)

    for i, program in enumerate(programs, 1):
        print(f"\nПрограмма #{i}:")
        print(f"   📍 Направление: {program['num_dir'] if program['num_dir'] else 'НЕ НАЙДЕНО'}")
        print(f"   🎓 Бюджет: {'✅' if program['has_budget'] else '❌'} ({program['count_budget']} мест)")
        print(f"   💰 Платно: {'✅' if program['has_contract'] else '❌'} ({program['count_contract']} мест)")
        if program['education_cost_from']:
            price_text = f"{program['education_cost_from']:,}".replace(',', ' ')
            print(f"   💸 Стоимость: {price_text} руб./год")
        else:
            print(f"   💸 Стоимость: не указана")
        print(f"link: {program['link_po']}")