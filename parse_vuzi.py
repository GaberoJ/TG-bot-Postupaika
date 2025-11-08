import requests
from bs4 import BeautifulSoup
import time


class Vuzi():
    """Для удобства вытаскивания информации про конкретный вуз"""
    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.city = None


def pagination(base_url, max_pages):
    """Создаем список ссылок на вузы при пагинации"""
    page_urls = [base_url]

    for page in range(2, max_pages + 1):
        page_url = f"{base_url}?page_num={page}"
        page_urls.append(page_url)
    return page_urls


def parse_vuzi_from_page(url):
    """Парсит вузы с одной страницы"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        current_url = response.url
        if 'page_num' not in current_url and url != "https://postupi.online/vuzi/":
            print(f"Редирект на главную страницу: {url} -> {current_url}")
            return []

        vuz_names = soup.find_all('h2', class_='list__h')
        page_vuzi = []

        for h2_elem in vuz_names:
            a_elem = h2_elem.find('a')
            if a_elem:
                name = a_elem.text.strip()
                link = a_elem['href']
                page_vuzi.append(Vuzi(name, link))

        print(f"Со страницы {url} получено {len(page_vuzi)} вузов")
        return page_vuzi

    except Exception as e:
        print(f"Ошибка при парсинге страницы {url}: {e}")
        return []


def get_city_for_vuz(vuz):
    """Получаем город для одного вуза"""
    try:
        response = requests.get(vuz.link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        city_elem = soup.find('p', class_='bg-nd__pre')
        vuz.city = city_elem.text.strip() if city_elem else "Город не найден"
        return True

    except Exception as e:
        print(f"Ошибка при получении города для {vuz.name}: {e}")
        vuz.city = "Ошибка"
        return False


if __name__ == "__main__":
    base_url = "https://postupi.online/vuzi/"
    lst_of_vuzes = []

    print("Генерируем URL страниц с пагинацией")
    page_urls = pagination(base_url, max_pages=2)  # Всего 58 страниц (включая base_url)
    print(f"Будет обработано страниц: {len(page_urls)}")

    print("\nПарсим вузы со всех страниц...")
    for i, page_url in enumerate(page_urls, 1):
        print(f"Обрабатываем страницу {i}/{len(page_urls)}")
        page_vuzi = parse_vuzi_from_page(page_url)
        lst_of_vuzes.extend(page_vuzi)
        time.sleep(0.5)

    print(f"\nВсего собрано вузов: {len(lst_of_vuzes)}")

    print("\nПолучаем города для каждого университета...")
    print("=" * 50)

    for i, vuz in enumerate(lst_of_vuzes, 1):
        success = get_city_for_vuz(vuz)
        if not success:
            break
        if i % 10 == 0:
            print(f"Прогресс: вуз {i}/{len(lst_of_vuzes)}")
            time.sleep(1)

    print("\nГотово! Все данные собраны.")
    # print("\nРезультаты:")
    # for i, vuz in enumerate(lst_of_vuzes, 1):
    #     print(f"{i}. {vuz.name} | {vuz.city} | {vuz.link}")
