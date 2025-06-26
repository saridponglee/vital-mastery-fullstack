from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import User
from .serializers import (
    UserSerializer, UserDetailSerializer, 
    LoginSerializer, RegistrationSerializer
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint.
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        return Response({
            'user': UserDetailSerializer(user).data,
            'message': 'Successfully logged in'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint.
    """
    logout(request)
    return Response({
        'message': 'Successfully logged out'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def session_view(request):
    """
    Check current user session.
    """
    if request.user.is_authenticated:
        return Response({
            'isAuthenticated': True,
            'user': UserDetailSerializer(request.user).data
        })
    
    return Response({
        'isAuthenticated': False,
        'user': None
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    User registration endpoint.
    """
    serializer = RegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        return Response({
            'user': UserDetailSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile.
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class AuthorListView(generics.ListAPIView):
    """
    List all authors (users who can create articles).
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return User.objects.filter(is_author=True, is_active=True) 