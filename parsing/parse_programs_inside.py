import requests
from bs4 import BeautifulSoup
import re


def parse_program_details(program_url):
    print(f"\n🔍 Парсим детали программы: {program_url}")

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    session.headers.update(headers)

    try:
        response = session.get(program_url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        result = {
            'name': None,
            'education_form': [],
            'education_lvl': None,
            'short_description': None
        }

        # 1. Название программы
        h2_tag = soup.find('h2', class_='h-large-nd')
        if h2_tag:
            match = re.search(r'["«](.+?)["»]', h2_tag.text.strip())
            result['name'] = match.group(1) if match else None

        # 2. Форма обучения и уровень образования из деталей
        detail_box = soup.find('div', class_='detail-box')
        if detail_box:
            for item in detail_box.find_all('div', class_='detail-box__item'):
                header = item.find('span', class_='detail-box__h')
                if not header:
                    continue

                header_text = header.text.strip()
                value_div = item.find('div')
                if not value_div:
                    continue

                if 'Уровень образования' in header_text:
                    value_span = value_div.find('span')
                    result['education_lvl'] = value_span.text.strip() if value_span else None

                elif 'Форма обучения' in header_text:
                    forms = []
                    # Ищем в ссылках
                    for link in value_div.find_all('a'):
                        forms.append(link.text.strip().lower())

                    # Ищем в спанках
                    if not forms:
                        for span in value_div.find_all('span'):
                            forms.append(span.text.strip().lower())

                    # Ищем в тексте
                    if not forms and value_div.text.strip():
                        forms = [f.strip().lower() for f in value_div.text.strip().split(',')]

                    result['education_form'] = [f.rstrip(',') for f in forms]

        # 3. Описание программы
        program_header = soup.find(['p', 'h2', 'h3', 'h4'], class_='h-large-nd', string='О программе')
        if program_header:
            descr_div = program_header.find_next('div', class_='descr-max')
            if descr_div:
                full_text = descr_div.get_text(' ', strip=True)
                # Ищем первое предложение
                match = re.search(r'^[^.!?]+[.!?]', full_text)
                result['short_description'] = match.group(0).strip() if match else full_text[:200].strip()

        # Вывод результатов
        # print(f"  ✓ Название: {result['name']}")
        # print(f"  ✓ Форма обучения: {result['education_form']}")
        # print(f"  ✓ Уровень: {result['education_lvl']}")
        # print(f"  ✓ Описание: {result['short_description']}" if result[
        #     'short_description'] else "  ✗ Описание: не найдено")

        return result

    except Exception as e:
        print(f"  ✗ Ошибка при парсинге: {e}")
        return {
            'name': None,
            'education_form': [],
            'education_lvl': None,
            'short_description': None
        }


if __name__ == "__main__":
    test_url = "https://spb.postupi.online/vuz/spbrsi/programma/355/"
    parse_program_details(test_url)