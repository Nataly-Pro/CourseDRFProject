from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habit
        exclude = ('owner',)

    def validate(self, data):
        if data['related_to']:
            if data['reward']:
                raise ValidationError(
                    'Одновременный выбор связанной привычки и указание вознаграждения некорректно.'
                )
            if not data['related_to'].is_nice:
                raise ValidationError(
                    'В связанные привычки могут попадать только привычки с признаком приятной привычки.'
                )
        if data['is_nice']:
            if data['reward'] or data['related_to']:
                raise ValidationError(
                    'У приятной привычки не может быть вознаграждения или связанной привычки.'
                )
        return data
