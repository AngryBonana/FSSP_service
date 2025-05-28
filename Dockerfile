FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем весь проект
COPY FSSP_site/ /app/

ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=FSSP_site.settings

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 