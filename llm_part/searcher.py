import requests
import time
import os
import json
from typing import List
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googlesearch import search


load_dotenv()
yandex_api_key = os.getenv("YANDEX_API_KEY")
folder_id = os.getenv("FOLDER_ID")

def create_queries(name: str, company: str, city: str, post: str) -> List[str]:
    """Создание поисковых запросов.
    
    Args:
        name (str): ФИО представителя компании.
        company (str): Название компании.
        city (str): Город расположения компании.
        post (str): Должность представителя компании.
    
    Returns:
        List[str]: Список из пяти поисковых запросов для поиска представителя компании.
    """
    queries = list()
    
    try:
        prompt ={
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
    default_queries =[
        f"site:vk.com {name} {post} {clear_company} {city}",
        f"site:linkedin.com {name} {post} {clear_company} {city}",
        f"{name} {company} {city}",
        f"site:twitter.com {name} {clear_company} {city}",
        f"site:facebook.com {name} {post} {clear_company} {city}",
    ]
    
    return default_queries
    

def yandex_search(queries: List[str], num_links: int = 10) -> List[str]:
    """Ищет ссылки на возможные соцсети представителя компании.

    Args:
        queries (List[str]): Список запросов, по которым будет производиться поиск.
        num_links (int): Число желаемых ссылок. 

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
            for card in soup.find_all("div", class_="VanillaReact OrganicTitle OrganicTitle_size_l organic__title-wrapper")[:10]:
                item_link = card.find("a", class_="Link Link_theme_normal OrganicTitle-Link organic__url link")["href"]
                links.append(item_link)
    
    links = list(set(links))
    if len(links) > num_links:
        return links[:num_links]
    return links 
        

def anylize_with_gpt(data):
    pass


# Пример использования
if __name__ == "__main__":
    name = "Мешков Максим Николаевич"
    post = "Генеральный Директор"
    city = "Воронеж"
    company = 'ООО "РЕСТОР"'
    queries = create_queries(name, company, city, post)
    print(yandex_search(queries=queries, num_links=5))