import requests
from typing import List
import os
import json
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
    

def google_search(queries: List[str]) -> List[str]:
    pass


def anylize_with_gpt(data):
    pass


# Пример использования
if __name__ == "__main__":
    name = "Мешков Максим Николаевич"
    post = "Генеральный Директор"
    city = "Воронеж"
    company = 'ООО "РЕСТОР"'
    print(create_queries(name, company, city, post))