from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

from .serializers import UserSerializer
from .models import User
from django.contrib.auth import get_user_model



class IsAuthenticatedOrPostOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return super().has_permission(request, view)
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        # Tambahkan pengecekan untuk is_deleted di sini
        if user.is_deleted:
            raise serializers.ValidationError("User account has been deleted.")

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class BlacklistRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        RefreshToken(refresh_token).blacklist()
        return Response("Success", status=status.HTTP_200_OK)
    
class UserView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrPostOnly]

    def post(self, request):
        data = request.data
        username_exists = User.objects.filter(username=data.get('username')).exists()
        email_exists = User.objects.filter(email=data.get('email')).exists()
        if username_exists or email_exists:
            error_message = {}
            if username_exists:
                error_message['username'] = ['Username already exists.']
            if email_exists:
                error_message['email'] = ['Email already exists.']
            
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user_id = request.user.id
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'message':'data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

        

