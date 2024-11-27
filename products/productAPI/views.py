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
    """
    Custom permission class for controlling product access.
    Allows all users to view products, while only authenticated users with appropriate permissions
    can add, update, or delete products.
    """
    def has_permission(self, request, view):
        user = request.user
        if  request.method == 'GET':
            #all users can view products even if they are not authenticated
                    return True
        elif user and user.is_authenticated: 
            #only SU and authenticated users having the right permissions can add, update and delete products
            if user.is_superuser:
                return True
            
            match request.method :
                case 'POST':
                    return user.has_perm('products.add_product')
                case 'PUT' | 'PATCH':
                    return user.has_perm('products.change_product')
                case 'DELETE':
                    return user.has_perm('products.delete_product')
        return False
    
class ProductFilter(FilterSet):
    """
    FilterSet for filtering products based on category, price range, and stock availability.
    """
    category = NumberFilter(field_name='category', lookup_expr='exact')
    price_min = NumberFilter(field_name='price', lookup_expr='gte')
    price_max = NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = BooleanFilter(field_name='stock_quantity', lookup_expr='gt', label='In stock')

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max', 'in_stock']

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product resources.
    Provides CRUD operations, filtering, searching, and pagination functionality.
    """
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
    @action(detail=True, methods=['delete'], url_path='delete-all-images')
    def delete_all_images(self, request, pk=None):
        """
        Deletes all images associated with the specified product.
        """
        try:
            product = self.get_object()
        except NotFound:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete all images associated with the product
        images_count = product.images.count()
        if images_count == 0:
            return Response({"message": "No images to delete."}, status=status.HTTP_404_NOT_FOUND)

        product.images.all().delete()
        return Response({"message": f"Deleted all {images_count} images successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete-specific-images')
    def delete_specific_images(self, request, pk=None):
        """
        Deletes specific images associated with the specified product.
        """
        try:
            product = self.get_object()
        except NotFound:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if image IDs are provided in the request data
        image_ids = request.data.get('image_ids', [])
        if not image_ids:
            return Response({"detail": "No image IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter and delete the specified images
        images_to_delete = product.images.filter(id__in=image_ids)  # Assuming `images` is a related name
        if not images_to_delete.exists():
            return Response({"detail": "No matching images found for deletion."}, status=status.HTTP_404_NOT_FOUND)

        images_deleted_count = images_to_delete.count()
        images_to_delete.delete()
        return Response({"message": f"Deleted {images_deleted_count} images successfully."}, status=status.HTTP_200_OK)