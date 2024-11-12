from rest_framework import serializers
from products.models import Product
from wishlist.models import Wishlist
from django.core.validators import MinValueValidator

class WishlistSerializer(serializers.ModelSerializer):

    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)
    class Meta:
        
        model = Wishlist
        fields = ['id','name','user','products','created_date']
        read_only_fields = ['id', 'user','created_date']
    
class AddProductToWishlistSerializer(serializers.Serializer):
        # serilaizer for adding/removing product to wishlist
        product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
