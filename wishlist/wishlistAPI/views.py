from rest_framework import viewsets, permissions
from wishlist.models import Wishlist
from .serializers import WishlistSerializer
from rest_framework.permissions import BasePermission

class ModelPermissions(BasePermission):
    from rest_framework.permissions import BasePermission

class ModelPermissions(BasePermission):
    """
    Custom permission class for controlling data access:
    - All users can CRUD (Create, Read, Update, Delete) only their own objects.
    - Staff users and Superusers can only read (GET) all objects, but cannot create, update, or delete them.
    """

    def has_permission(self, request, view):
        """
        This method checks if the user has permission to access the view.
        Allows all users to perform GET requests (view data).
        Other methods (POST, PUT, DELETE) are allowed only for authenticated users.
        """

        if request.user.is_authenticated and request.method == 'GET':
            return True  # Allow all users to view data
        return request.user and request.user.is_authenticated  # Allow authenticated users for other methods

    def has_object_permission(self, request, view, obj):
        """
        This method checks if the user has permission to access a specific object.
        """

        # Case 1: Staff or Superuser can only view (GET) the object but cannot modify it
        if request.user.is_staff or request.user.is_superuser:
            if request.method == 'GET':
                return True  # Allow GET request for staff or superuser
            return False  # Disallow non-GET requests (POST, PUT, DELETE)

        # Case 2: Authenticated user can only access their own object (CRUD)
        if request.user.is_authenticated:
            if obj.user == request.user:  # Only the owner of the object can perform actions
                return True  # Allow CRUD actions for the object owner (GET, POST, PUT, DELETE)
        return False  # Disallow access for others (non-authenticated or non-matching user)

    
class WishlistViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Wishlist instances.
    """

    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Override the get_queryset method to filter wishlists based on the user.
        """
        # If the user is a staff or superuser, allow them to see all wishlists
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Wishlist.objects.all()
        
        # For regular authenticated users, only show their own wishlists
        return Wishlist.objects.filter(user=self.request.user)


    def perform_create(self, serializer):
        """
        Override the perform_create method to automatically associate the wishlist with the current user.
        """
        serializer.save(user=self.request.user)