from rest_framework.permissions import BasePermission


class IsSelfUser(BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        else:
            return False
