from dadata import Dadata
import os
from dotenv import load_dotenv


load_dotenv()
dadata_key = os.getenv("DADATA_API_KEY")


def get_company_info_by_inn(inn: str, api_key: str = dadata_key, secret_key: str = None) -> dict:
    """
    Получает данные организации из ЕГРЮЛ по ИНН через API DaData.

    :param inn: ИНН организации (12 цифр)
    :param api_key: API-ключ от DaData
    :param secret_key: Секретный ключ (если нужен)
    :return: Данные о представителе (ФИО, Должность)
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
        return f"Ошибка при запросе к DaData: {e}"

# Пример использования
if __name__ == "__main__":
    inn = "3663141298"

    company_data = get_company_info_by_inn(inn)
    print(company_data)