from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .permission import IsParent, IsTutor

from .helpers import get_tokens_for_user, token_blacklisted, send_email_verification
from .models import User, TutorProfile, ParentProfile
from .serializers.account_serializer import TutorProfileSerializer, ParentProfileSerializer, UserSerializer

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
    

"""
Login API endpoint 

- POST: login with email or username and password. Return user data and token if login successfully.
  While login, check if user is active or not. If not, return message 'Please verify your email'
"""
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
                if user.is_active == False:
                    return Response({'message': 'Please verify your email'}, status=status.HTTP_400_BAD_REQUEST)
                
                token = get_tokens_for_user(user)
                role = user.role

                if role == 'tutor':
                    tutor = TutorProfile.objects.get(user=user)
                    serializer = TutorProfileSerializer(tutor)
                elif role == 'parent':
                    parent = ParentProfile.objects.get(user=user)
                    serializer = ParentProfileSerializer(parent)
                elif role == 'admin':
                    serializer = UserSerializer(user)
                
                return Response({'data': serializer.data, 'token': token}, status=status.HTTP_200_OK)

            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

"""
Register API endpoint

- POST: register new user with role [tutor, parent, admin]. Return user data and message if register successfully.
  If role != admin, send email verification to user. If failed to send email, delete the user and return error message.
"""
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user')
        if not user_data:
            return Response({'message': 'User data must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        role = user_data.get('role')
        if role not in ['tutor', 'parent', 'admin']:
            return Response({'message': 'Invalid or missing role'}, status=status.HTTP_400_BAD_REQUEST)
        
        if role == 'tutor':
            serializer = TutorProfileSerializer(data=request.data)
        elif role == 'parent':
            serializer = ParentProfileSerializer(data=request.data)
        elif role == 'admin':
            serializer = UserSerializer(data=request.data)
        else:
            return Response({'message': 'Role must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            user = serializer.save()
            if (role != 'admin'):
                try:
                    user = user.user
                    send_email_verification(user, request)
                except Exception as e:
                    User.objects.get(user_id=user.user_id).delete()
                    print (str(e))
                    return Response({'message': 'Failed to send email verification with error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({'data': serializer.data, 'message': 'Please verify your email'}, status=status.HTTP_201_CREATED) 
            return Response({'data': serializer.data, 'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
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
        
class ActivateAccountView(View):

    def get(self, request):
        token = request.GET.get('token', None)
        if token is None:
            return Response({'message': 'Token must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        login_redirect_url = request.build_absolute_uri('/login/')
        re_verify_url = request.build_absolute_uri('/api/reverify-email/')
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(user_id=user_id)
            user.is_active = True
            user.save()
            return render(request, 'account_activated.html', context={'redirect_url': login_redirect_url})
        except Exception as e:
            return render(request, 'activated_failed.html', context={'re_verify_url': re_verify_url, 'error': str(e)})
        
class ReverifyEmailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        email = request.query_params.get('email', None)
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({'message': 'Your account is already activated'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                send_email_verification(user, request)
                login_redirect_url = request.build_absolute_uri('/login/')
                return Response({'message': 'Email verification sent successfully', 'redirect_url': login_redirect_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        user_id = request.user.user_id
        user = User.objects.get(user_id=user_id)
        role = user.role

        if role == 'tutor':
            tutor = TutorProfile.objects.get(user=user)
            serializer = TutorProfileSerializer(tutor, data=request.data, partial=True)
        elif role == 'parent':
            parent = ParentProfile.objects.get(user=user)
            serializer = ParentProfileSerializer(parent, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            avatar_url = request.build_absolute_uri(serializer.instance.avatar.url)
            return Response({'message': 'Avatar uploaded successfully', 'avatar_url': avatar_url}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TutorView(BaseView):
    model = TutorProfile
    serializer = TutorProfileSerializer
    permission_classes = [IsAuthenticated, IsTutor]

class ParentView(BaseView):
    model = ParentProfile
    serializer = ParentProfileSerializer
    permission_classes = [IsAuthenticated, IsParent]
    