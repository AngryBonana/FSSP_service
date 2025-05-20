import requests
import time
import os
import json
from typing import List
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()
yandex_api_key = os.getenv("YANDEX_API_KEY")


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
            "modelUri": "gpt://b1gmogi5kl7jvign6303/yandexgpt",
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
        f"site:instagram.com {name} {city}",
        f"site:twitter.com {name} {clear_company} {city}",
        f"site:facebook.com {name} {post} {clear_company} {city}",
    ]
    
    return default_queries
    

def google_search(queries: List[str], num_links: int = 5) -> List[str]:
    """Ищет ссылки на возможные соцсети представителя компании.

    Args:
        queries (List[str]): Список запросов, по которым будет производиться поиск.
        num_links (int): Число желаемых ссылок. 

    Returns:
        List[str]: Список ссылок на возможные соцсети представителя компании.
    """
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    links = list()
    for query in queries:
        time.sleep(3)
        query = "+".join(query.split(' '))
        URL = f"https://www.google.com/search?q={query}"
        print(URL)
        headers = {"user-agent": USER_AGENT}
        try:
            response = requests.get(url=URL, headers=headers)
        except Exception as e:
            print(f"Не удалось обработать запрос. Ошибка: {e}") # TODO: Почему-то не проходит запрос нормально, из-за этого не получается спарсить
            continue
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            for result in soup.find_all("div", class_=".yuRUbf"):
                print(100)
                link = result.find('a')['href']
                if link.startswith('/url?q='):
                    link = link[7:].split('&')[0]
                if not link.startswith('http'):
                    continue
                links.append(link)
    
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
    queries = ['Мешков Максим Николаевич Воронеж',
               'Мешков Максим Николаевич ООО «РЕСТОР»',
               'Мешков Максим Николаевич Генеральный Директор Воронеж',
               'Мешков Максим Николаевич профиль в социальных сетях',
               'ООО «РЕСТОР» Воронеж Максим Мешков Генеральный Директор профиль в соцсетях']
    print(queries)
    print(google_search(queries=queries))