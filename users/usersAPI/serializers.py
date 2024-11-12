from rest_framework import serializers
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id','username', 'email', 'password', 'is_superuser', 'is_staff', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}
        

    def create(self, validated_data):
        currentUser = self.context['request'].user
        if not currentUser.is_superuser: 
            # If the user is not a superuser, prevent changes to is_staff and is_superuser
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)

        user = User(
            username = validated_data['username'],
            email = validated_data['email'], 
            is_superuser= validated_data['is_superuser'],
            is_staff=  validated_data['is_staff'] ,
            #is_active=  validated_data['is_active'] 
            )
        user.set_password(validated_data['password'])
        user.save()
        return user
    def update(self, instance, validated_data):
        currentUser = self.context['request'].user
        if not currentUser.is_superuser: 
            # If the user is not a superuser, prevent changes to is_staff and is_superuser
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)

        if not currentUser.is_superuser: #only super user can define if the user is suoeruser or staff
            validated_data['is_superuser']=False
            validated_data['is_staff']= False
        return super().update(instance, validated_data)
    
    