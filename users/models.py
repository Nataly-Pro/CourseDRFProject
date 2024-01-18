from django.contrib.auth.models import AbstractUser
from django.db import models

from habits.models import NULLABLE


class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True, verbose_name='почта')
    tg_chat_id = models.CharField(max_length=10, verbose_name='телеграмм_id')
    first_name = models.CharField(max_length=20, verbose_name='имя')
    avatar = models.ImageField(verbose_name='аватар', **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('id',)
