from celery import shared_task
from django.conf import settings
from datetime import datetime, date
from ..models import Card
from .api_parser import ArbitrAPIParser
from .LLM.searcher import analyze_parsed

@shared_task
def run_arbitr_parser():
    """
    Задача для запуска парсера арбитражных дел
    """
    try:
        parser = ArbitrAPIParser(
            api_key=settings.KAD_API_KEY,
            max_requests=settings.KAD_MAX_REQUESTS
        )
        parser.run(date_from=date.today().strftime("%Y-%m-%d"))
        analyze_parsed()
    except Exception as e:
        print(f"Ошибка при выполнении парсера: {e}")
        raise


# For prodaction
# Запуск ежденвного парсинга (
# celery -A your_project worker -l info
# celery -A your_project beat -l info
# то же самое для ллм