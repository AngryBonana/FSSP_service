from django.contrib.auth.models import AbstractUser
from django.db import models


class SiteText(models.Model):
    name = models.CharField('Название текста', max_length=100, unique=True)
    content = models.TextField('Содержание')
    updated = models.DateTimeField('Последнее обновление', auto_now=True)

    class Meta:
        verbose_name = 'Текст сайта'
        verbose_name_plural = 'Тексты сайта'

    def __str__(self):
        return self.name