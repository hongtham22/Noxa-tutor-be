from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .permission import IsParent, IsTutor

from .helpers import get_tokens_for_user, token_blacklisted
from .models import User, TutorProfile, ParentProfile
from .serializers.account_serializer import TutorProfileSerializer, ParentProfileSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated



"""
APIView for CRUD object based on User mode
- model: model to be used [TutorProfile, ParentProfile]
- serializer: serializer to be used [TutorProfileSerializer, ParentProfileSerializer]

* method get: get all objects or get object by id[pk]
* method post: create new object: created by calling create method in serializer
* method put: update object by id[pk] : updated by calling update method in serializer
* method delete: delete object by id[pk] : delected User object by id[pk], then automatically deleted TutorProfile or ParentProfile object because of on_delete=models.CASCADE in User model
"""

class BaseView(APIView):
    model = None
    serializer = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes] 

    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, user_id=pk)
            instance = get_object_or_404(self.model, user=user)
            serializer = self.serializer(instance)
        else:
            instances = self.model.objects.all()
            serializer = self.serializer(instances, many=True)
        
        return Response(serializer.data)
    
    def put(self, request, pk):
        user = get_object_or_404(User, user_id=pk)
        instance = get_object_or_404(self.model, user=user)
        serializer = self.serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = get_object_or_404(User, user_id=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', None)
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        try:
            # Check if email or username is provided
            if email:
                user = User.objects.filter(Q(email=email)).first()
            elif username:
                user = User.objects.filter(Q(username=username)).first()
            else:
                return Response({'message': 'Either email or username must be provided'}, status=status.HTTP_400_BAD_REQUEST)

            # If user found, check the password
            if user and user.check_password(password):
                return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)

            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        role = request.data.get('user', None).get('role', None)
        if role == 'tutor':
            serializer = TutorProfileSerializer(data=request.data)
        elif role == 'parent':
            serializer = ParentProfileSerializer(data=request.data)
        else:
            return Response({'message': 'Role must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh', None)
            if token_blacklisted(refresh_token):
                return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)  
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTutor])
def foo_tutor(request):
    return Response({'message': 'You are authenticated'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsParent])
def foo_parent(request):
    return Response({'message': 'You are authenticated'}, status=status.HTTP_200_OK)

class TutorView(BaseView):
    model = TutorProfile
    serializer = TutorProfileSerializer
    permission_classes = [IsAuthenticated, IsTutor]

class ParentView(BaseView):
    model = ParentProfile
    serializer = ParentProfileSerializer
    permission_classes = [IsAuthenticated, IsParent]
    