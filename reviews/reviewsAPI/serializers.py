from rest_framework import serializers
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_date']
        read_only_fields = ['user', 'created_date']  # `user` and `created_date` should be read-only
