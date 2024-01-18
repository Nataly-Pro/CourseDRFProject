import requests
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from habits.models import Habit


@shared_task
def send_tg_message():
    """
    Отправляет пользователю (создателю привычки) сообщение в Telegramm
    с напоминанием о выполнении запланированного действия.
    """

    url = f'https://api.telegram.org/bot{settings.TG_BOT_API_KEY}/sendMessage'
    # вычисление параметров для фильтрации привычек по времени выполнения,
    # чтобы запустить уведомление мин. за 10 минут до старта запланированного действия,
    # но не дублировать при следующем цикле задачи.
    default_timezone = timezone.get_default_timezone()
    min_time = datetime.now(default_timezone) + timedelta(minutes=10)
    task_interval = settings.CELERY_BEAT_SCHEDULE['send_tg_message']['schedule']
    max_time = min_time + task_interval
    time_filter = {'start_time__gte': min_time,
                   'start_time__lt': max_time}

    for habit in Habit.objects.filter(**time_filter):
        # корректировка для отображения времени в уведомлении по МСК
        start_time = habit.start_time + timedelta(hours=3)
        # данные для запроса
        chat_id = habit.owner.tg_chat_id
        data = {'chat_id': chat_id,
                'text': f'Не забудь, сегодня в {start_time.hour}ч. и '
                        f'{start_time.minute}мин. по МСК нужно {habit.action}'}
        try:
            response = requests.post(url, data)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            print("Что-то пошло не так:(")
        finally:
            if habit.interval == 'ежедневно':
                habit.start_time += timedelta(days=1)
            elif habit.interval == 'раз в 2 дня':
                habit.start_time += timedelta(days=2)
            elif habit.interval == 'раз в 3 дня':
                habit.start_time += timedelta(days=3)
            elif habit.interval == 'раз в неделю':
                habit.start_time += timedelta(days=7)
            habit.save(update_fields=['start_time'])
