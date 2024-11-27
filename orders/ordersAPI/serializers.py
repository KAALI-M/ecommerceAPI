from rest_framework import serializers
from orders.models import Order

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    """
    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'quantity', 'order_date']
        read_only_fields = ['order_date', 'user']

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

        # Ensure product and quantity are provided
        if not product or not quantity:
            raise serializers.ValidationError("Product and quantity must be specified.")

        # Validate stock availability
        if quantity > product.stock_quantity:  # Assuming `stock_quantity` is a field in Product
            raise serializers.ValidationError(
                f"Ordered quantity ({quantity}) exceeds available stock ({product.stock_quantity})."
            )

        return data

    def create(self, validated_data):
        """
        Custom create method to reduce stock when an order is placed.
        """
        product = validated_data['product']
        quantity = validated_data['quantity']

        # Reduce the stock
        product.stock_quantity -= quantity
        product.save()

        # Create the order
        return super().create(validated_data)
