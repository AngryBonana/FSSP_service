import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from ..models import Card
from django.contrib.auth.models import User
import time


class ArbitrAPIParser:
    def __init__(self, api_key: str, max_requests: int = 20):
        """
        Инициализация парсера
        :param api_key: ключ API
        :param max_requests: максимальное количество запросов за один запуск
        """
        self.base_url = "https://parser-api.com/parser/arbitr_api"
        self.api_key = api_key
        self.max_requests = max_requests
        self.request_count = 0
        self.session = requests.Session()
        
        # Получаем или создаем системного пользователя для парсера
        self.system_user, _ = User.objects.get_or_create(
            username='system_parser',
            defaults={'is_staff': True}
        )

    def _increment_request_counter(self, success: bool = True) -> bool:
        """
        Увеличивает счетчик запросов и проверяет лимит
        :param success: был ли запрос успешным
        :return: можно ли делать еще запросы
        """
        if success:
            self.request_count += 1
        return self.request_count < self.max_requests

    def search_cases(self, date_from: str = None, date_to: str = None, 
                    page: int = 1) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Поиск дел по параметрам
        :return: (список дел, флаг возможности продолжения запросов)
        """
        if not self._increment_request_counter(False):
            print("Достигнут лимит запросов")
            return [], False

        params = {
            'key': self.api_key,
            'page': page,
            'DateFrom': date_from,
            'DateTo': date_to
        }

        try:
            print(f"Отправка запроса к {self.base_url}/search")
            print(f"Параметры запроса: {params}")
            
            response = self.session.get(
                f"{self.base_url}/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('Success') == 1:
                can_continue = self._increment_request_counter(True)
                return data.get('Cases', [])[:self.max_requests - self.request_count], can_continue
            else:
                error_msg = data.get('error', 'Неизвестная ошибка')
                error_code = data.get('error_code', 'Нет кода')
                print(f"Ошибка API: {error_msg} (код: {error_code})")
                return [], False
                
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка подключения к API: {e}")
            print("Пожалуйста, проверьте:")
            print("1. Правильность URL API")
            print("2. Доступность сервиса")
            print("3. Подключение к интернету")
            return [], False
        except requests.exceptions.Timeout as e:
            print(f"Превышено время ожидания ответа от API: {e}")
            return [], False
        except Exception as e:
            print(f"Ошибка при поиске дел: {e}")
            return [], False

    def process_case_data(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка данных о деле
        """
        # Получаем информацию об ответчике
        respondents = case.get('Respondents', [])
        respondent_info = respondents[0] if respondents else {}
        
        # Формируем контент
        content_parts = []
        if respondent_info:
            content_parts.append(f"Ответчик: {respondent_info.get('Name', 'Не указан')}")
            if respondent_info.get('Address'):
                content_parts.append(f"Адрес: {respondent_info['Address']}")
        
        # Добавляем информацию о состоянии дела
        if case.get('State'):
            content_parts.append(f"Состояние: {case['State']}")
            
        # Добавляем информацию о суде
        if case.get('Court'):
            content_parts.append(f"Суд: {case['Court']}")
            
        # Добавляем информацию о типе дела
        if case.get('CaseType'):
            content_parts.append(f"Тип дела: {case['CaseType']}")
        
        return {
            'external_id': case.get('CaseId', ''),
            'title': f"Дело №{case.get('CaseNumber', '')}",
            'content': '\n'.join(content_parts),
            'source_url': f"https://kad.arbitr.ru/Card/{case.get('CaseId', '')}"
        }

    def save_to_database(self, case_data: Dict[str, Any]) -> None:
        """
        Сохраняет данные о деле в базу
        """
        try:
            card, created = Card.objects.get_or_create(
                external_id=case_data['external_id'],
                defaults={
                    'title': case_data['title'],
                    'content': case_data['content'],
                    'source_url': case_data['source_url'],
                    'created_by': self.system_user,
                    'is_active': True,
                    'order': 0
                }
            )
            
            if not created:
                card.title = case_data['title']
                card.content = case_data['content']
                card.source_url = case_data['source_url']
                card.save()
                
        except Exception as e:
            print(f"Ошибка при сохранении в базу данных: {e}")

    def run(self, date_from: str = None, date_to: str = None) -> None:
        """
        Запускает процесс получения и обработки данных
        """
        if not date_from:
            date_from = date.today().strftime("%Y-%m-%d")
        if not date_to:
            date_to = date_from

        print(f"Начинаем получение дел за период {date_from} - {date_to}...")
        print(f"Доступно запросов: {self.max_requests}")
        
        # Получаем список дел
        cases, can_continue = self.search_cases(
            date_from=date_from,
            date_to=date_to
        )
        
        if not cases:
            print("Не найдено дел за указанный период")
            return

        print(f"Найдено {len(cases)} дел")
        print(f"Использовано запросов: {self.request_count}/{self.max_requests}")
        
        for i, case in enumerate(cases, 1):
            print(f"\nОбработка дела {i}/{len(cases)}")
            
            if case.get('Respondents'):
                respondent = case['Respondents'][0]
                processed_data = self.process_case_data(case)
                self.save_to_database(processed_data)
                print(f"Дело сохранено (Ответчик: {respondent.get('Name', 'Не указан')})")
            else:
                print("Дело пропущено: нет данных об ответчике")
            
            if not self._increment_request_counter(False):
                print("\nДостигнут лимит запросов. Завершаем работу.")
                break
            
            # Добавляем задержку между запросами
            time.sleep(1)
        
        print(f"\nПарсинг завершен. Всего использовано запросов: {self.request_count}/{self.max_requests}") 