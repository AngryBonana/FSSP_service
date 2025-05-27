# Руководство пользователя FSSP Parser


## Установка и запуск

### Предварительные требования
- Docker и Docker Compose
- Git (для получения исходного кода)
- Свободный порт 8000 на компьютере
- Минимум 2GB оперативной памяти


1. Настройка переменных окружения:
   - Создайте файл `.env` в корневой директории проекта
   - Заполните следующие переменные:
```env
DEBUG=1
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=FSSP_site.settings
CELERY_BROKER_URL=redis://redis:6379/0
KAD_API_KEY=your-kad-api-key-here
KAD_MAX_REQUESTS=17
YANDEX_API_KEY=your-yandex-api-key-here
FOLDER_ID=your-folder-id-here
```

2. Запуск проекта:
```bash
# Сборка контейнеров
docker-compose build

# Запуск системы
docker-compose up -d
```

3. Первоначальная настройка:
```bash
# Применение миграций
docker-compose exec web python FSSP_site/manage.py migrate

# Создание администратора
docker-compose exec web python FSSP_site/manage.py createsuperuser
```

