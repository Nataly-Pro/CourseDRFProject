from datetime import timedelta

from django.conf import settings
from django.db import models

from habits.validators import validate_duration


NULLABLE = {'blank': True, 'null': True}

INTERVAL_TYPES = (
    ('ежедневно', 'ежедневно'),
    ('раз в 2 дня', 'раз в 2 дня'),
    ('раз в 3 дня', 'раз в 3 дня'),
    ('еженедельно', 'еженедельно'),
)


class Habit(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='создатель', **NULLABLE)
    place = models.CharField(max_length=100, verbose_name='место выполнения')
    start_time = models.DateTimeField(verbose_name='время начала')
    action = models.CharField(max_length=100, verbose_name='действие')
    is_nice = models.BooleanField(default=False, verbose_name='приятная', **NULLABLE)
    related_to = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='связанная с другой', **NULLABLE)
    interval = models.CharField(default='ежедневно', max_length=50,
                                choices=INTERVAL_TYPES, verbose_name='периодичность')
    reward = models.CharField(max_length=300, verbose_name='вознаграждение', **NULLABLE)
    duration = models.DurationField(default=timedelta(seconds=120), validators=[validate_duration],
                                    verbose_name='продолжительность')
    is_public = models.BooleanField(default=False, verbose_name='публичная')

    def __str__(self):
        return self.action

    class Meta:
        verbose_name = 'привычка'
        verbose_name_plural = 'привычки'
        ordering = ('id',)
