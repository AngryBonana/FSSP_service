from celery import shared_task
from api_parser import ArbitrAPIParser
from django.conf import settings
from datetime import datetime, date
from ..models import Card
from LLM.searcher import *

@shared_task
def run_arbitr_parser():
    parser = ArbitrAPIParser(api_key=settings.ARBIR_API_KEY)
    parser.run(date_from=date.today().strftime("%Y-%m-%d"))
    analyze_parsed()


# For prodaction
# Запуск ежденвного парсинга (
# celery -A your_project worker -l info
# celery -A your_project beat -l info
# то же самое для ллм