from rest_framework import serializers
from orders.models import Order
from products.models import Product 

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    Attributes:
        read_only_fields: Add order_date as read-only field.
    """

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'quantity', 'order_date']
        read_only_fields = ['order_date']

    def validate_quantity(self, value):
        """
        Validate that the quantity is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value

    def validate(self, data):
        """
        Object-level validation to ensure business rules are met.
        Example: Check if ordered quantity does not exceed stock.
        """
        product = data.get('product')
        quantity = data.get('quantity')

        # Ensure product and quantity are provided (useful if required=False in fields)
        if not product or not quantity:
            raise serializers.ValidationError("Product and quantity must be specified.")

        # Validate stock availability
        if quantity > product.stock_quantity:  # Assuming `stock` is a field in the Product model
            raise serializers.ValidationError(
                f"Ordered quantity ({quantity}) exceeds available stock ({product.stock_quantity})."
            )

        return data