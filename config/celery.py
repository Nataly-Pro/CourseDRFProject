from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установка переменной окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра объекта Celery
app = Celery('config')

# Загрузка настроек из файла Django
# Использование здесь строки означает, что рабочему процессу не нужно сериализовать
# объект конфигурации дочерним процессам.
# namespace='CELERY' означает, что все ключи конфигурации, связанные с Celery,
# должны иметь префикс `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django
app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True
