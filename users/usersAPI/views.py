from rest_framework.permissions import BasePermission
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer

class ModelPermissions(BasePermission):
    """
    Custom permission class to define user access control for CRUD operations on user objects.
    Methods:
    - has_permission(request, view): Determines if the user has general access to the requested operation.
    - has_object_permission(request, view, obj): Determines if the user has access to perform the operation on a specific object.
    """
    def has_permission(self, request, view):            
        """
        Determines if the user has permission to perform the requested operation.
        
        - POST: Allows any user to create a new user.
        - GET: Allows authenticated users to view user information.
        - PUT, PATCH, DELETE: Allows authenticated users to modify user information.

        Args:
            request: The request object containing the HTTP method and user information.
            view: The view object being accessed.

        Returns:
            bool: True if the operation is permitted, False otherwise.
        """
        if request.method == 'POST' :  # Everyone can create a new user
            return True
        elif request.method == 'GET':
            return request.user.is_authenticated  # if the super user the query will be set to all if not will be set to user.id
        elif request.method in ('PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False


    def has_object_permission(self, request, view, obj):

        """
        Checks if the user has permission to access a specific user object.

        This method ensures that only the owner of the object or a superuser can
        access the object. If the request is a GET request, the user can view
        their own object. If the request is a PUT, PATCH, or DELETE request, the
        user must be a superuser or the owner of the object to perform the
        operation.

        Args:
            request: The request object.
            view: The viewset object.
            obj: The user object being accessed.

        Returns:
            True if the user has permission to access the object, False otherwise.
        """
        if request.method in ('GET', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_superuser or (request.user == obj)
        return False


class UsersViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing user objects.
    This viewset provides default actions for creating, retrieving, updating, and deleting user objects.
    It also provides custom permissions to control access to the user objects.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [ModelPermissions]

    def get_queryset(self):
        
        """
        Returns a filtered queryset of users based on the request user's permissions.
        
        If the request user is a superuser, the entire queryset is returned.
        Otherwise, the queryset is filtered to include only the request user's
        objects.
        """    
        # Check if the request is a GET and the view action is 'list'
        if self.request.method == 'GET' and self.action == 'list':
            return self.queryset.filter(id=self.request.user.id)

        # Default behavior for other cases
        return self.queryset