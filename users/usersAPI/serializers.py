from rest_framework import serializers
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Handles serialization and deserialization of User objects.
    Provides custom `create` and `update` methods to enforce role-based restrictions 
    (e.g., only superusers can modify `is_staff` and `is_superuser` fields).
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_superuser', 'is_staff', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}  # Ensures password is write-only and not included in response data.

    def create(self, validated_data):
        """
        Create and return a new User instance.
        - Ensures `is_superuser` and `is_staff` fields are only set if the current user is a superuser.
        - Sets `is_active` to True by default.

        Args:
            validated_data (dict): Validated data from the request.

        Returns:
            User: A new user instance.
        """
        currentUser = self.context['request'].user  # Retrieve the current authenticated user.

        # Remove `is_staff` and `is_superuser` from validated_data if the current user is not a superuser.
        if not currentUser.is_superuser:
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)

        # Create the user instance with basic fields.
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=True  # Default to active status.
        )
        
        # Set `is_superuser` and `is_staff` fields only if the current user is a superuser.
        if currentUser.is_superuser:
            user.is_superuser = validated_data.get('is_superuser', False)
            user.is_staff = validated_data.get('is_staff', False)
        else:
            user.is_superuser = False
            user.is_staff = False

        # Hash and set the user's password, then save the instance to the database.
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing User instance.
        - Restricts modification of `is_staff` and `is_superuser` fields for non-superusers.
        - Ensures non-superusers cannot grant themselves or others elevated privileges.

        Args:
            instance (User): The existing user instance to update.
            validated_data (dict): Validated data from the request.

        Returns:
            User: The updated user instance.
        """
        currentUser = self.context['request'].user  # Retrieve the current authenticated user.

        # Remove `is_staff` and `is_superuser` fields from validated_data for non-superusers.
        if not currentUser.is_superuser:
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)

        # Enforce non-superuser privileges (explicitly set `is_superuser` and `is_staff` to False).
        if not currentUser.is_superuser:
            validated_data['is_superuser'] = False
            validated_data['is_staff'] = False

        # Perform the default update behavior and return the updated instance.
        return super().update(instance, validated_data)
