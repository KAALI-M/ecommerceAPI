from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from products.models import Product, Image
from products.productAPI.serializers import ProductSerializer
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .pagination import CustomPagination
from django_filters.rest_framework import FilterSet, NumberFilter, BooleanFilter
from rest_framework.exceptions import NotFound


class ModelPermissions(permissions.DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user
        if  request.method == 'GET':
            #all users can view products even if they are not authenticated
                    return True
        elif user and user.is_authenticated: 
            #only authenticated users having the right permissions can add, update and delete products
            match request.method :
                case 'POST':
                    return user.has_perm('products.add_product')
                case 'PUT':
                    return user.has_perm('products.change_product')
                case 'DELETE':
                    return user.has_perm('products.delete_product')
        return False
    
class ProductFilter(FilterSet):
    category = NumberFilter(field_name='category', lookup_expr='exact')
    price_min = NumberFilter(field_name='price', lookup_expr='gte')
    price_max = NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = BooleanFilter(field_name='stock_quantity', lookup_expr='gt', label='In stock')

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max', 'in_stock']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name'] # Allows partial match on the `name` field
    pagination_class = CustomPagination  

    #exemple :  GET /api/products/?category=1
    #exemple :  GET /api/products/?search=product&category=1&page=2&page_size=10
    #/api/products/?category=1&price_min=10&price_max=100&in_stock=true&search=product&page=2&page_size=10
   
   
    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        try:
            # Retrieve the product instance using pk
            product = self.get_object()  # This automatically raises a 404 if not found
        except NotFound:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if images are provided in the request
        files = request.FILES.getlist('images')
        if not files:
            return Response({"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Create an image instance for each file
        for file in files:
            Image.objects.create(product=product, image=file)

        return Response({"message": "Images uploaded successfully"}, status=status.HTTP_201_CREATED)