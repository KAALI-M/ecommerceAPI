from rest_framework import viewsets
from categories.models import Category
from categories.categoriesAPI.serializers import ProductCategorySerializer
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

class ModelPermissions(permissions.DjangoModelPermissions):
    """
    Custom permission class for controlling product access.
    Allows all users to view products, while only authenticated users with appropriate permissions
    can add, update, or delete products.
    """
    def has_permission(self, request, view):
        user = request.user
        if  request.method == 'GET':
            #all users can view categories even if they are not authenticated
                    return True
        elif user is not None and user.is_authenticated: 
            #only SU and authenticated users having the right permissions can add, update and delete products categories
            if user.is_superuser:
                return True
            else:
                match request.method :
                    case 'POST':
                        return user.has_perm('categories.add_category')
                    case 'PUT' | 'PATCH':
                        return user.has_perm('categories.change_category')
                    case 'DELETE':
                        return user.has_perm('categories.delete_category')
        return False
    
class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product resources.
    Provides CRUD operations, filtering, searching, and pagination functionality.
    """
    queryset = Category.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [ModelPermissions]


   
   
