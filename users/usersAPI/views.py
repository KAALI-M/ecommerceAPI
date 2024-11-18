from rest_framework.permissions import BasePermission
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer

class UserCRUDPermissions(BasePermission):
    """
    Custom permission class to define user access control for CRUD operations on user objects.

    Methods:
    - has_permission(request, view): Determines if the user has general access to the requested operation.
    - has_object_permission(request, view, obj): Determines if the user has access to perform the operation on a specific object.
    """

    def has_permission(self, request, view):
        """
        Checks if the user has general permissions for the requested action.

        Permissions:
        - POST: Anyone can create a new user account.
        - GET, PUT, PATCH, DELETE: Only authenticated users can access these methods.

        Parameters:
        request (Request): The current HTTP request object.
        view (View): The view instance that is handling the request.

        Returns:
        bool: True if the request is allowed, False otherwise.
        """
        if request.method == 'POST':  # Everyone can create a new user
            return True
        elif request.method in ('GET', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user has permissions for the requested action on a specific object.

        Object-level permissions:
        - GET, PUT, PATCH, DELETE: Allowed for superusers or if the user is acting on their own profile.

        Parameters:
        request (Request): The current HTTP request object.
        view (View): The view instance that is handling the request.
        obj (Object): The object being accessed.

        Returns:
        bool: True if the object-level operation is allowed, False otherwise.
        """
        if request.method in ('GET', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_superuser or (request.user.id == obj.id)
        return False


class UsersViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing user objects, providing CRUD functionality with custom permissions.

    Attributes:
    - queryset: The queryset of all User objects in the database.
    - serializer_class: The serializer class used for validating and serializing user data.
    - permission_classes: A list of permission classes applied to this viewset.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserCRUDPermissions]
