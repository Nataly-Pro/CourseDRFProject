from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class UserAPITest(APITestCase):

    def setUp(self):
        self.data = {
            'email': 'Anna@mail.ru',
            'password': '357951',
            'tg_chat_id': '1234567890',
            'first_name': 'Anna',
            'is_active': True
        }

    def test_create(self):
        """ Тестирование регистрации пользователя """

        response = self.client.post('/users/', self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):
        """ Тестирование редактирования данных пользователя """

        self.user_1 = User.objects.create(**self.data)
        self.access_token = str(RefreshToken.for_user(self.user_1).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.patch(f'/users/{self.user_1.pk}/', {'first_name': 'Test'})

        self.user_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user_1.first_name, 'Test')

    def test_get_user(self):
        """ Тестирование получения данных другого пользователя. """

        self.user_1 = User.objects.create(**self.data)
        self.data['email'] = 'user_2@gmail.com'
        self.user_2 = User.objects.create(**self.data)
        self.access_token = str(RefreshToken.for_user(self.user_2).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(f'/users/{self.user_1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
