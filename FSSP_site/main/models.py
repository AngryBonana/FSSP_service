from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    source_url = models.URLField(verbose_name="URL источника", blank=True, null=True)
    parsed_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата парсинга")
    external_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Внешний ID")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-parsed_date', 'order']
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['parsed_date']),
        ]

    def __str__(self):
        return self.title