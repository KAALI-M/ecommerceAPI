from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User, Group
from users.usersAPI.serializers import UserSerializer
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission



class UserCRUDPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':  #every one can create new user
            return True
        elif request.method in ('GET','PUT','PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET','PUT','PATCH', 'DELETE'):
            return request.user.is_superuser or (request.user.id == obj.id)
        return False


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserCRUDPermissions]



   
