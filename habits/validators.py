from datetime import timedelta

from rest_framework import serializers


def validate_duration(value):
    if value > timedelta(seconds=120):
        raise serializers.ValidationError('Время выполнения должно быть не более 120 секунд')


# class CompatibilityValidator:
#
#     def __init__(self, field):
#         self.field = field
#
#     def __call__(self, value):
#         tmp_val = dict(value).get(self.field)
#         if tmp_val:
#             :
#                 raise ValidationError('URL should be youtube.com')
