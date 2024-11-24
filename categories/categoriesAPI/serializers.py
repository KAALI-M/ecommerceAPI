from rest_framework import serializers
from django.core.validators import MinValueValidator
from categories.models import Category

class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for Category resource."""
    class Meta:
        model = Category
        fields = ['id', 'name']
