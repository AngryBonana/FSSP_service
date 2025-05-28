import requests
import json
from typing import List
from bs4 import BeautifulSoup
from main.models import Card
from django.conf import settings
import re

def create_queries(folder_id: str, yandex_api_key: str, name: str, company: str, city: str, post: str) -> List[str]:
    """Генерирует пять посковых запросов.

    Args:
        folder_id (str): Идентификатор каталога в Yandex Cloud.
        yandex_api_key (str): API-ключ от Яндекса.
        name (str): ФИО представителя компании.
        company (str): Название компании.
        city (str): Город расположения компании.
        post (str): Должность представителя компании.

    Returns:
        List[str]: Список из пяти поисковых запросов для поиска представителя компании.
    """
    queries = list()

    try:
        prompt = {
            "modelUri": f"gpt://{folder_id}/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "300",
                "reasoningOptions": {
                    "mode": "DISABLED"
                }
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты ассистент для генерации поисковых запросов"
                },
                {
                    "role": "user",
                    "text": f"""Создай пять поисковых запросов для поиска страниц в социальных сетях – например, ВКонтакте, LinkedIn, Instagram, Facebook – человека по следующим данным:
                    ФИО: {name}
                    Место работы: {company}
                    Должность: {post}
                    Город: {city}
                    В ответе укажи только пять поисковых запросов, каждый с новой строки"""
                }
            ]
        }
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {yandex_api_key}"
        }

        response = requests.post(url=url, headers=headers, json=prompt)
        data = json.loads(response.text)

        gpt_ans = data["result"]["alternatives"][0]["message"]["text"]
        queries = gpt_ans.split("\n")

        return [q.strip() for q in queries]

    except Exception as e:
        print(f"При обращении к gemini для создания запросов произошла ошибка {e}")

    clear_company = company.replace('"', " ")
    default_queries = [
        f"site:vk.com {name} {post} {clear_company} {city}",
        f"site:linkedin.com {name} {post} {clear_company} {city}",
        f"{name} {company} {city}",
        f"site:twitter.com {name} {clear_company} {city}",
        f"site:facebook.com {name} {post} {clear_company} {city}",
    ]

    return default_queries


def yandex_search(folder_id: str, yandex_api_key: str, queries: List[str], num_links=30) -> List[str]:
    """Ищет ссылки на возможные соцсети представителя компании.

    Args:
        folder_id (str): Идентификатор каталога в Yandex Cloud.
        yandex_api_key (str): API-ключ от Яндекса.
        queries (List[str]): Список запросов, по которым будет производиться поиск.
        num_links (int): Число желаемых ссылок, может вернуть меньше, если не найдено достаточное число ссылок.

    Returns:
        List[str]: Список ссылок на возможные соцсети и контактные данные представителя компании.
    """
    links = list()

    for query in queries:
        print(f"Поиск по запросу {query}")
        query = "+".join(query.split())
        URL = f"https://yandex.ru/search/xml/html?folderid={folder_id}&apikey={yandex_api_key}&query=%3C{query}%3E&filter=strict&page=1"
        print(URL)
        try:
            response = requests.get(URL)
        except Exception as e:
            print(f"Не удалось обработать запрос. Ошибка: {e}")
            continue
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.find_all("div",
                                      class_="VanillaReact OrganicTitle OrganicTitle_size_l organic__title-wrapper")[
                        :15]:
                item_link = card.find("a", class_="Link Link_theme_normal OrganicTitle-Link organic__url link")["href"]
                links.append(item_link)

    links = list(set(links))
    if len(links) > num_links:
        return links[:num_links]
    return links


def anylize_with_gpt(folder_id: str, yandex_api_key: str, links: List[str], name: str, company: str, city: str,
                     post: str, num_links: int = 5) -> List[str]:
    """Анализирует прикрепленные ссылки с помощью gpt и возвращает наиболее полезные.

    Args:
        folder_id (str): Идентификатор каталога в Yandex Cloud.
        yandex_api_key (str): API-ключ от Яндекса.
        links (List[str]): Список ссылок, где предполагаемо могут быть контактные данные представителя юрлица.
        name (str): ФИО представителя компании.
        company (str): Название компании.
        city (str): Город расположения компании.
        post (str): Должность представителя компании.
        num_links (int): Количество желаемых на выходе ссылок.

    Returns:
        List[str]: Список полезных ссылок.
    """
    if num_links > len(links):
        num_links = len(links)
    good_links = list()

    try:
        prompt = {
            "modelUri": f"gpt://{folder_id}/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": "600",
                "reasoningOptions": {
                    "mode": "DISABLED"
                }
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты ассистент для анализа ссылок"
                },
                {
                    "role": "user",
                    "text": f"""Проверь ссылки на наличие полезных данных о человеке.
                    Под полезными данными считается информация, которая поможет найти контактные данные человека.
                    Вот информация о человеке:
                    ФИО: {name}
                    Место работы: {company}
                    Должность: {post}
                    Город: {city}
                    Вот ссылки:
                    {links}
                    В ответе укажи следующее количество наиболее подходящих ссылок – {num_links}.
                    Каждая ссылка должны быть с новой строки без каких либо дополнительных символов."""
                }
            ]
        }
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {yandex_api_key}"
        }

        response = requests.post(url=url, headers=headers, json=prompt)
        data = json.loads(response.text)

        gpt_ans = data["result"]["alternatives"][0]["message"]["text"]
        good_links = gpt_ans.split("\n")

        return [l.strip() for l in good_links]

    except Exception as e:
        print(f"Не удалось обработать запрос с помощью gpt. Возвращаю первые {num_links} ссылок.")
    return links[:num_links]

def analyze_parsed():
    yandex_api_key = settings.YANDEX_API_KEY
    folder_id = settings.FOLDER_ID

    names_with_titles = Card.objects.all()

    GPT_LINKS = 30
    for i in names_with_titles:
        tmp = str(i.Address).split(',')[3].split(' ')
        city = tmp[len(tmp) - 1]
        comp_name = i.Name
        queries = create_queries(folder_id=folder_id, yandex_api_key=yandex_api_key, name='Неизвестно',
                                 company=comp_name,
                                 city=city, post='Руководитель')
        #
        links = yandex_search(folder_id=folder_id, yandex_api_key=yandex_api_key, queries=queries, num_links=2)
        ans = anylize_with_gpt(folder_id, yandex_api_key, links, 'Неизвестно', comp_name, city, 'Руководитель',
                               num_links=GPT_LINKS)

        def extract_text(data):
            """
            Извлекает текст из сложной структуры данных, удаляя Markdown-ссылки
            """

            def process_item(item):
                if isinstance(item, str):
                    # Удаляем Markdown-ссылки вида [текст](url)
                    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', item)
                    return text.strip()
                elif isinstance(item, (list, tuple, set)):
                    return ' '.join(process_item(x) for x in item)
                elif isinstance(item, dict):
                    return ' '.join(process_item(v) for v in item.values())
                return ''

            result = process_item(data)
            # Удаляем лишние пробелы
            return result

        ans = extract_text(ans)
        templ = '\n\nАнанлиз от ИИ\n\n'
        if i.content.count(templ):
            # remove if exists
            i.content = i.content.split(templ)[0]
            pass

        i.content = i.content + f"{templ}{ans}"
        i.save()
        print(i.content)
