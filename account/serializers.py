from rest_framework import serializers
from .models import User
from django.contrib.auth import password_validation
from django.core import exceptions


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        user = User(**data)

        password = data.get('password')
        errors = dict()
        try:
            password_validation.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
             errors['password'] = list(e.messages)

        if errors:
             raise serializers.ValidationError(errors)
        return super(UserSerializer, self).validate(data)
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return user