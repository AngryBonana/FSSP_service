from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Card(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    Name = models.TextField(verbose_name="Имя")
    Address = models.TextField(verbose_name="Адрес")
    source_url = models.URLField(verbose_name="URL источника", blank=True, null=True)
    parsed_date = models.DateTimeField(verbose_name="Дата парсинга")
    external_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Внешний ID")
    is_active = models.BooleanField(default=True, verbose_name="Актвна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inn = models.CharField(
        max_length=12,  # ИНН может быть 10 или 12 цифр
        blank=True,
        null=True,
        verbose_name="ИНН"
    )
    class Meta:
        ordering = ['order']
        ordering = ['-parsed_date', 'order']
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['parsed_date']),
        ]

    def __str__(self):
        return self.title


class FilterDate(models.Model):
    filter_date = models.DateField(
        verbose_name="Дата фильтрации",
        default=timezone.now,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(
        verbose_name="Активный фильтр",
        default=False,
        help_text="Если отмечено, карточки будут фильтроваться по этой дате"
    )

    class Meta:
        verbose_name = "Дата фильтрации"
        verbose_name_plural = "Даты фильтрации"
        ordering = ['-filter_date']

    def __str__(self):
        return f"Фильтр от {self.filter_date.strftime('%d.%m.%Y')}"