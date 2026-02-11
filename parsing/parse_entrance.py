import requests
from bs4 import BeautifulSoup
import re


def parse_passing_grades(program_url):
    """
    Парсит проходные баллы со страницы программы для бюджета и контракта отдельно.
    Возвращает словарь с данными для бюджета и контракта:
    - budget: данные для бюджетных мест
    - contract: данные для платных мест
    Каждый содержит: passing_grade, average_passing_grade, num_of_exams, latest_year
    """

    session = requests.Session()
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

    result = {
        'budget': {
            'passing_grade': None,
            'average_passing_grade': None,
            'num_of_exams': None,
            'latest_year': None
        },
        'contract': {
            'passing_grade': None,
            'average_passing_grade': None,
            'num_of_exams': None,
            'latest_year': None
        }
    }

    try:
        response = session.get(program_url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Ищем контейнеры для бюджета и контракта
        # Бюджетные места: класс scoreFree
        # Платные места: класс scorePay

        # 1a. Бюджетные места
        budget_containers = soup.find_all('div', class_='scoreFree')

        for container in budget_containers:
            # Ищем заголовок со статистикой
            header = container.find('p', class_='score-box__h')
            if header:
                # Извлекаем год из заголовка
                text = header.text.strip()
                year_match = re.search(r'\b(20\d{2})\b', text)
                if year_match:
                    result['budget']['latest_year'] = int(year_match.group(1))

                # Ищем баллы в этом контейнере
                score_items = container.find_all('div', class_='score-box__item')

                for item in score_items:
                    span_text = item.find('span')
                    if not span_text:
                        continue

                    text = span_text.text.strip()
                    score_span = item.find('span', class_='score-box__score')

                    if score_span:
                        score_text = score_span.text.strip()
                        numbers = re.findall(r'\b(\d+)\b', score_text)

                        if numbers:
                            number = int(numbers[0])

                            if 'Проходной балл' in text:
                                result['budget']['passing_grade'] = number
                            elif 'Средний проходной балл' in text:
                                result['budget']['average_passing_grade'] = number

        # 1b. Платные места
        contract_containers = soup.find_all('div', class_='scorePay')

        for container in contract_containers:
            # Ищем заголовок со статистикой
            header = container.find('p', class_='score-box__h')
            if header:
                # Извлекаем год из заголовка
                text = header.text.strip()
                year_match = re.search(r'\b(20\d{2})\b', text)
                if year_match:
                    result['contract']['latest_year'] = int(year_match.group(1))

                # Ищем баллы в этом контейнере
                score_items = container.find_all('div', class_='score-box__item')

                for item in score_items:
                    span_text = item.find('span')
                    if not span_text:
                        continue

                    text = span_text.text.strip()
                    score_span = item.find('span', class_='score-box__score')

                    if score_span:
                        score_text = score_span.text.strip()
                        numbers = re.findall(r'\b(\d+)\b', score_text)

                        if numbers:
                            number = int(numbers[0])

                            if 'Проходной балл' in text:
                                result['contract']['passing_grade'] = number
                            elif 'Средний проходной балл' in text:
                                result['contract']['average_passing_grade'] = number

        # 2. Вычисляем num_of_exams для каждого типа
        for grade_type in ['budget', 'contract']:
            passing = result[grade_type]['passing_grade']
            average = result[grade_type]['average_passing_grade']

            if passing and average and average > 0:
                result[grade_type]['num_of_exams'] = passing // average

        # 3. Если нашли данные только в одном контейнере (например, только budget),
        #    но есть класс hidden в другом, все равно сохраняем только найденные данные
        return result

    except Exception as e:
        print(f"Ошибка при парсинге {program_url}: {e}")
        return result


# Пример использования и тестирования
if __name__ == "__main__":
    # Тестовый URL с бюджетом и контрактом
    test_url = "https://msk.postupi.online/vuz/mgudt/programma/2307/"

    print(f"Тестируем: {test_url}")
    print("=" * 60)

    grades = parse_passing_grades(test_url)

    print("\n📊 БЮДЖЕТНЫЕ МЕСТА:")
    print(f"  Проходной балл: {grades['budget']['passing_grade']}")
    print(f"  Средний проходной балл: {grades['budget']['average_passing_grade']}")
    print(f"  Количество экзаменов: {grades['budget']['num_of_exams']}")
    print(f"  Год статистики: {grades['budget']['latest_year']}")

    print("\n📊 ПЛАТНЫЕ МЕСТА:")
    print(f"  Проходной балл: {grades['contract']['passing_grade']}")
    print(f"  Средний проходной балл: {grades['contract']['average_passing_grade']}")
    print(f"  Количество экзаменов: {grades['contract']['num_of_exams']}")
    print(f"  Год статистики: {grades['contract']['latest_year']}")