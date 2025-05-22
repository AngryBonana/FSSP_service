from typing import Dict
from dadata import Dadata
import os
from dotenv import load_dotenv


load_dotenv()
dadata_key = os.getenv("DADATA_API_KEY")


def get_company_info_by_inn(inn: str, api_key: str, secret_key: str = None) -> Dict:
    """Получает данные организации из ЕГРЮЛ по ИНН через API DaData.

    Args:
        inn (str): ИНН организации (12 цифр).
        api_key (str): API-ключ от DaData.
        secret_key (str): Секретный ключ (если нужен).
        
    Returns:
        Dict: Словарь с данными о компании, поля: company, inn, address, city, name, post.
    """
    try:
        dadata = Dadata(api_key, secret_key)
        result = dadata.find_by_id("party", inn)
        if not result:
            return "Организация с таким ИНН не найдена."
        result = result[0] # Первое совпадение – наша компания
        company = result["value"]
        name = result["data"]["management"]["name"]
        post = result["data"]["management"]["post"]
        address = result["data"]["address"]["unrestricted_value"]
        city = result["data"]["address"]["data"]["city"]
        # print(result)
        
        data = {
            'company': company,
            'inn': inn,
            'address': address,
            'city': city,
            'name': name,
            'post': post.title(),
        }
        
        return data
    
    except Exception as e:
        print(f"Ошибка при запросе к DaData: {e}")
    return None

# Пример использования
if __name__ == "__main__":
    inn = "3663141298"

    company_data = get_company_info_by_inn(inn, api_key=dadata_key)
    print(company_data)