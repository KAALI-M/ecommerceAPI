from rest_framework import serializers
from products.models import Product,Image
from django.core.validators import MinValueValidator

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id','image']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product resource.
    Handles validation and nested relationships with images.
    """
    images = ProductImageSerializer(many=True, read_only = True) # Nested serializer for related images
    class Meta:
        model = Product
        fields = ['id','name','description','price','stock_quantity','created_date','category', 'images']
        #validations 
        name = serializers.CharField(required=True, error_messages={'required': 'Name is required.'})
        price = serializers.DecimalField(
            required=True,
            max_digits=10,
            decimal_places=2,
            error_messages={'required': 'Price is required.'},
            validators=[MinValueValidator(0.01)]  # Ensure price is positive
        )
        stock_quantity = serializers.IntegerField(
            required=True,
            error_messages={'required': 'Stock quantity is required.'},
            validators=[MinValueValidator(1)]  # Ensure stock quantity is positive
        )

