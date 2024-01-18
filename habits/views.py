from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.paginators import HabitPaginator
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def perform_create(self, serializer):
        new_habit = serializer.save()
        new_habit.owner = self.request.user
        new_habit.save()

    def get_permissions(self):
        if self.action in ['list', 'create']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsOwner]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            own_habits = Habit.objects.filter(owner=user)
            habits = Habit.objects.filter(is_public=True)
            return own_habits.union(habits).order_by('id',)
        else:
            own_habits = Habit.objects.filter(owner=user).order_by('id',)
            return own_habits
