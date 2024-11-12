from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from wishlist.models import Wishlist, Product
from wishlist.wishlistAPI.serializers import WishlistSerializer, AddProductToWishlistSerializer
from rest_framework.permissions import IsAuthenticated
from .pagination import CustomPagination


class WishlistViewSet(viewsets.ModelViewSet):
    queryset  = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  

    def get_queryset(self):
        #ensure user can only acces their own wishlist
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Set the wishlist's user to the authenticated user
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        # Add a product to the wishlist
        wishlist = self.get_object()
        serializer = AddProductToWishlistSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.validated_data['product_id']
            wishlist.products.add(product)
            return Response({"message": "Product added to wishlist."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_product(self, request, pk=None):
        # Remove a product from the wishlist
        wishlist = self.get_object()
        serializer = AddProductToWishlistSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.validated_data['product_id']
            wishlist.products.remove(product)
            return Response({"message": "Product removed from wishlist."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)