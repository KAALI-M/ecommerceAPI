from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from reviews.models import Review, Product
from reviews.reviewsAPI.serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated

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

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [ModelPermissions]  # Only authenticated users can submit reviews

    def get_queryset(self):
        # Filter reviews by product if `product_id` is passed as a URL parameter
        product_id = self.request.query_params.get('product', None)
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        # Set the `user` field to the currently authenticated user
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Additional validation (optional): Ensure rating is within range (1-5)
        rating = request.data.get('rating')
        if rating and (int(rating) < 1 or int(rating) > 5):
            return Response({"detail": "Rating must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)
