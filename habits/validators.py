from datetime import timedelta

from rest_framework import serializers


def validate_duration(value):
    if value > timedelta(seconds=120):
        raise serializers.ValidationError('Время выполнения должно быть не более 120 секунд')
