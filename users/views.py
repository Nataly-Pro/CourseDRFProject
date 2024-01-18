from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from users.models import User
from users.permissions import IsSelfUser
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsSelfUser]
        else:
            self.permission_classes = [IsAdminUser]

        return [permission() for permission in self.permission_classes]
