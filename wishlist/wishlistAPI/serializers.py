from rest_framework import serializers
from wishlist.models import Wishlist
from products.models import Product

class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for Wishlist model.
    Transforms Wishlist data into JSON and validates incoming data.
    """

    # We don't want to include the created_date in updates, so it's read-only.

    class Meta:
        model = Wishlist
        fields = ['id', 'name', 'user','products', 'created_date']
        read_only_fields = ['created_date']
        extra_kwargs = {'user': {'required': False}}  # Make user field optional
        
    def validate(self, data):
        """
        Perform additional validations for the wishlist creation.
        """

        # Ensure the user is provided in the request and matches the current user.
        user = self.context['request'].user
        if data.get('user') is None : # no user included in the request
            data['user'] = user
        elif data['user'] != user:
            raise serializers.ValidationError("You cannot create a wishlist for another user.")
        return data
