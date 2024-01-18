from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='tomova@mail.ru',
            tg_chat_id='1234567890',
            first_name='Admin',
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )

        user.set_password('159357[p')
        user.save()
