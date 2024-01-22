from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from habits.models import Habit
from habits.serializers import HabitSerializer
from users.models import User


class HabitsAPITestCase(APITestCase):

    def setUp(self):
        """ Подготовка тестовой базы """

        super().setUp()
        self.user = User.objects.create(
            email='Test@mail.ru',
            tg_chat_id=settings.TG_CHAT_ID,
            first_name='Test',
            is_active=True
        )
        self.user.set_password('123456')
        self.user.save()
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.habit_1 = Habit.objects.create(
            place='Дом',
            action='Запланировать досуг на выходные',
            is_nice=True,
            related_to=None,
            interval='еженедельно',
            reward='',
            is_public=True,
            start_time='2024-01-17T07:39:00+03:00',
            owner=self.user
        )

        self.habit_2 = Habit.objects.create(
            place='Работа',
            action='Тестирование',
            is_nice=False,
            related_to=self.habit_1,
            interval='ежедневно',
            reward='',
            is_public=False,
            start_time='2024-01-17T07:11:00+03:00',
            owner=self.user
        )

    def test_create(self):
        """ Тестирование создания привычки """

        data = {
            'place': 'дом',
            'action': 'Тестирование',
            'is_nice': False,
            'related_to': '',
            'interval': 'ежедневно',
            'reward': 'отдых',
            'is_public': True,
            'start_time': '2024-01-16T08:01:00+03:00'
        }
        response = self.client.post('/habits/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {'id': 3, 'place': 'дом', 'start_time': '2024-01-16T08:01:00+03:00', 'action': 'Тестирование',
             'is_nice': False, 'interval': 'ежедневно', 'reward': 'отдых', 'duration': '00:02:00',
             'is_public': True, 'related_to': None
             }
        )
        serializer = HabitSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertTrue(Habit.objects.get(pk=3).owner == self.user)

    def test_serializers_validation(self):
        """ Тестирование проверок при создании/редактировании привычки """

        data_1 = {
            'place': 'дом',
            'action': 'Тестирование',
            'is_nice': False,
            'related_to': self.habit_1.id,
            'interval': 'ежедневно',
            'reward': 'отдых',
            'is_public': True,
            'start_time': '2024-01-16 08:01'
        }
        with self.assertRaises(ValidationError):
            serializer = HabitSerializer(data=data_1)
            serializer.is_valid(raise_exception=True)

        # меняем данные для создания привычки:
        # связка с неприятной привычкой habit_2
        data_1['related_to'] = self.habit_2.id
        data_1['reward'] = ''

        with self.assertRaises(ValidationError):
            serializer = HabitSerializer(data=data_1)
            serializer.is_valid(raise_exception=True)

        # меняем данные для создания привычки:
        # делаем её приятной и связанной с self.habit_1
        data_1['is_nice'] = True
        data_1['related_to'] = self.habit_1.id

        with self.assertRaises(ValidationError):
            serializer = HabitSerializer(data=data_1)
            serializer.is_valid(raise_exception=True)

        # меняем данные для создания привычки:
        # убираем связанную привычку, устанавливаем вознаграждение
        data_1['related_to'] = None
        data_1['reward'] = 'отдых'

        with self.assertRaises(ValidationError):
            serializer = HabitSerializer(data=data_1)
            serializer.is_valid(raise_exception=True)

        # меняем данные для создания привычки:
        # устанавливаем duration > 120
        data_1['duration'] = 121
        with self.assertRaises(serializers.ValidationError):
            serializer = HabitSerializer(data=data_1)
            serializer.is_valid(raise_exception=True)

    def test_get(self):
        """ Тестирование просмотра собственных привычек пользователя
         и несобственных публичных """

        # добавлен новый пользователь
        self.new_user = User.objects.create(
            email='New_Test@mail.ru',
            tg_chat_id='1234567890',
            first_name='New_Test',
            is_active=True
        )
        self.new_user.set_password('258963')
        self.new_user.save()

        # создана привычка не авторизованного пользователя
        self.habit_3 = Habit.objects.create(
            place='Дом',
            action='Выпить стакан воды',
            is_nice=False,
            related_to=None,
            interval='ежедневно',
            reward='Хорошее самочувствие',
            is_public=True,
            start_time='2024-01-18T08:01:00+03:00',
            owner=self.new_user
        )
        response = self.client.get('/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_update(self):
        """ Тестирование редактирования привычки """

        data = {
            'place': 'Дом',
            'action': 'планирование досуга',
            'is_nice': True,
            'related_to': '',
            'interval': 'ежедневно',
            'reward': '',
        }
        url = f'/habits/{self.habit_1.id}/'
        response = self.client.patch(url, data=data)
        self.habit_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.habit_1.interval, 'ежедневно')

    def test_retrieve(self):
        """ Тестирование просмотра 1 привычки"""

        response = self.client.get(f'/habits/{self.habit_1.pk}/')
        serializer_data = HabitSerializer(self.habit_1).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_delete(self):
        """ Тестирование удаления привычки"""

        response = self.client.delete(f'/habits/{self.habit_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TasksAPITestCase(APITestCase):

    def setUp(self):
        """ Подготовка тестовой базы """
        super().setUp()
        self.user = User.objects.create(
            email='Test@mail.ru',
            tg_chat_id='5564486290',
            first_name='Test',
            is_active=True
        )
        self.user.set_password('123456')
        self.user.save()
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.default_timezone = timezone.get_default_timezone()
        self.test_habit = Habit.objects.create(
            place='Не важно где',
            action='Запланировать досуг на выходные',
            is_nice=True,
            related_to=None,
            interval='еженедельно',
            reward='',
            is_public=True,
            start_time=datetime.now(self.default_timezone) + timedelta(minutes=10),
            owner=self.user
        )

    def test_task_send_tg_message(self):
        """ Тестирование периодической задачи send_tg_message """

        url = f'https://api.telegram.org/bot{settings.TG_BOT_API_KEY}/sendMessage'
        min_time = datetime.now(self.default_timezone) + timedelta(minutes=10)
        task_interval = settings.CELERY_BEAT_SCHEDULE['send_tg_message']['schedule']
        max_time = min_time + task_interval
        time_filter = {'start_time__gte': min_time,
                       'start_time__lt': max_time}

        for habit in Habit.objects.filter(**time_filter):
            start_time = habit.start_time + timedelta(hours=3)
            chat_id = habit.owner.tg_chat_id
            data = {'chat_id': chat_id,
                    'text': f'Не забудь, сегодня в {start_time.hour}ч. и {start_time.minute}мин. '
                            f'по МСК нужно {habit.action}'}
            response = requests.post(url, data)
            response.raise_for_status()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
