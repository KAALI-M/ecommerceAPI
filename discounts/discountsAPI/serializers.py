from rest_framework  import serializers
from discounts.models import Discount, ProductDiscount
from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        Model = Product
        fields = ['id','name','description','price','stock_quantity']

class DiscountSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductDiscount resource.
    """
    #products = productSerializer(many=True, read_only=True)

    Products = serializers.PrimaryKeyRelatedField(many=True,read_only=True)

    class Meta: 
        model = Discount
        fields = ['id','name','start_date','end_date','amount', 'Products']
        read_only_fields = ['id']

    
