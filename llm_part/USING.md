## Функционал

### `contact_find_by_inn.py`

#### Общие сведения

В файле одна функция `get_company_info_by_inn()`, которая по номеру ИНН возвращает информацию о юрлице:
- Название компании
- Адрес регистрации
- Имя представителя 
- Должность представителя
- ИНН компании

Параметры функции:
- inn – <b>строка</b> с номером ИНН
- api_key – API-ключ сервиса Dadata
- secret_key – секретный ключ сервиса Dadata (необязательный параметр)

#### Пример использования
Импортируем файл и подгружаем API-ключ из `.env` (либо можно создать переменную и поместить туда ключ)

```
import contact_find_by_inn as contact_find
import os
from dotenv import load_dotenv


load_dotenv()
dadata_key = os.getenv("DADATA_API_KEY")

print(contact_find.get_company_info_by_inn(api_key=dadata_key, inn="3663141298"))
```

#### Как это работает?

Для работы используется API сервиса Dadata. Оно имеет бесплатный вариант, где дается 10000 токенов в день. Один запрос тратит ~ 20-30 токенов.  
При необходимости есть платные подписки.

### `searcher.py`

#### Общие сведения
Файл содержит всего три функции.  
Разберем каждую по порядку.

`create_queries()` генерирует запросы с использованием Yandex GPT для поиска представителя компании в интернете.

Параметры:
- folder_id (str): Идентификатор каталога в Yandex Cloud.
- yandex_api_key (str): API-ключ от Яндекса.
- name (str): ФИО представителя компании.
- company (str): Название компании.
- city (str): Город расположения компании.
- post (str): Должность представителя компании.

Возвращает:
- Список из пяти поисковых запросов
<hr>

`yandex_search()` ищет поисковые запросы и возвращает список ссылок из результотов.

Параметры:
- `folder_id (str)`: Идентификатор каталога в Yandex Cloud.
- `yandex_api_key (str)`: API-ключ от Яндекса.
- `queries (list)`: Список запросов, по которым будет производиться поиск.
- `num_links (int)`: Число желаемых ссылок, может вернуть меньше, если не найдено достаточное число ссылок.

Возвращает:
- Список из `num_links` ссылок. Если было найдено меньше ссылок, то возращает все найденые.

<hr>

`anylize_with_gpt()` Анализирует ссылки и возвращает те, которые больше всего подходят для получения контактов человека.

Параметры:
- `folder_id (str)`: Идентификатор каталога в Yandex Cloud.
- `yandex_api_key (str)`: API-ключ от Яндекса.
- `links (list)`: Список ссылок, где предполагаемо могут быть контактные данные представителя юрлица.
- `name (str)`: ФИО представителя компании.
- `company (str)`: Название компании.
- `city (str)`: Город расположения компании.
- `post (str)`: Должность представителя компании.
- `num_links (int)`: Количество желаемых на выходе ссылок.

Возвращает:
- Список из `num_links` ссылок. Если было ссылок меньше, то возвращает все полученные.

#### Пример использования

```
import os
from dotenv import load_dotenv
import searcher


load_dotenv()

yandex_api_key = os.getenv("YANDEX_API_KEY")
folder_id = os.getenv("FOLDER_ID")

name = "Мешков Максим Николаевич"
post = "Генеральный Директор"
city = "Воронеж"
company = 'ООО "РЕСТОР"'

queries = create_queries(folder_id=folder_id, yandex_api_key=yandex_api_key, name=name, company=company, city=city, post=post)

links = yandex_search(folder_id=folder_id, yandex_api_key=yandex_api_key, queries=queries, num_links=30)

print(anylize_with_gpt(folder_id, yandex_api_key, links, name, company, city, post, num_links=10))
```

### Что нужно для работы?

Все требования прописаны в файле `requirements.txt`  
Вот список:
- requests
- python-dotenv
- dadata
- beatifulsoup4