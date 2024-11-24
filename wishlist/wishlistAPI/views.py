from rest_framework import viewsets, permissions
from wishlist.models import Wishlist
from .serializers import WishlistSerializer
from rest_framework.permissions import BasePermission


class ModelPermissions(permissions.BasePermission):
    """
    Custom permission to allow owners to CRUD their own objects.
    Staff and superusers can read all objects.
    """

    def has_permission(self, request, view):
        """
        Determines if the user has permission to perform the requested operation.

        - Allows any authenticated user to create a new wishlist.
        - Allows authenticated users to view their own wishlist.
        - Restricts modification and deletion to the object owner only.
        """
        # Only authenticated users can access these views
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Custom permission for object-level access:
        - Allow staff and superusers to read any object.
        - Allow owners to access safe methods on their objects.
        - Restrict modification and deletion to the object owner only.
        """
        # Allow staff and superusers to read any object
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff or request.user.is_superuser or obj.user.id == request.user.id
        # Only the owner can modify or delete their object
        return obj.user.id == request.user.id

    
class WishlistViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Wishlist instances.
    """

    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [ModelPermissions]

    def get_queryset(self):
        """
        Override the get_queryset method to filter wishlists based on the user.
        """
        # If the user is a staff or superuser, return all Objects
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        # Check if the request is a GET and the view action is 'list'
        if self.request.method == 'GET' and self.action == 'list':
            return self.queryset.filter(user=self.request.user)

        # Default behavior for other cases
        return self.queryset
        
    
    def perform_create(self, serializer):
        """
        Override the perform_create method to automatically associate the wishlist with the current user.
        """
        serializer.save(user=self.request.user)