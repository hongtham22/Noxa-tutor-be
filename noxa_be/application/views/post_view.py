from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsParent, IsTutor
from accounts.models import * 
from application.serializers.post_serializer import PostSerializer, ClassTimeSerializer
from application.serializers.job_registration_serializer import JobRegistrationSerializer
from application.serializers.class_serializer import ClassSerializer

from rest_framework.decorators import api_view, permission_classes
import unicodedata
import re
import time


"""
PostView API endpoint for JobPost model. Use for parent to CRUD their job posts.
"""

class PostView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()] 
        return [permission() for permission in self.permission_classes] 
    
    def get(self, request, pk=None):
        if pk:
            if User.objects.filter(user_id=pk).exists():
                user = get_object_or_404(User, user_id=pk)
                posts = JobPost.objects.filter(parent_id=user)
                post_serializer = PostSerializer(posts, many=True, context={'request_type': 'detail'})
            else:
                post = get_object_or_404(JobPost, post_id=pk)
                post_serializer = PostSerializer(post, context={'request_type': 'detail'})
                job_registerd = JobRegister.objects.filter(post_id=post)
                registration_serializer = JobRegistrationSerializer(job_registerd, many=True)
                
                data = post_serializer.data
                data['registration'] = registration_serializer.data
                return Response(data)
        else:
            if request.user.is_authenticated:
                user_id = request.user
                registered_posts = JobRegister.objects.filter(tutor_id=user_id)
                query = Q(status=Status.APPROVED) & ~Q(post_id__in=[post.post_id.post_id for post in registered_posts])
                posts = JobPost.objects.filter(query)
            else:
                posts = JobPost.objects.all()
            post_serializer = PostSerializer(posts, many=True, context={'request_type': 'detail'})
        return Response(post_serializer.data)
    
    def post(self, request):
        post_serializer = PostSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        post = get_object_or_404(JobPost, post_id=pk)
        post_serializer = PostSerializer(post, data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_object_or_404(JobPost, post_id=pk)
        post.delete()

        # check deleted in class_time
        class_times = ClassTime.objects.filter(post_id=pk)
        if not class_times:
            print ('Logic works perfectly')
        for class_time in class_times:
            class_time.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        start_time = time.time()
        params = {key.strip(): value for key, value in request.query_params.items()}
        text = params.get('text').strip()
        if not text:
            text = request.data.get('text')
            print ('Text in request data: ', text)
        posts = JobPost.objects.all()
        posts_serializer = PostSerializer(posts, many=True)
        result = []

        def matches_text(field_value):
            return self.remove_accents(text) in self.remove_accents(field_value)
        
        for post in posts_serializer.data:
            if any((
                matches_text(post['subject']),
                matches_text(post['grade']),
                matches_text(post['background_desired']),
                matches_text(post['session_per_week']),
                matches_text(post['wage_per_session']),
                matches_text(post['student_number']),
                matches_text(post['description']),
                matches_text(post['address']),
                self.search_in_profile(text, post)
            )):
                result.append(post)
                continue

            for class_time in post['class_times']:
                if any((
                    self.search_in_weekday(text, post),
                    matches_text(class_time['time_start']),
                    matches_text(class_time['time_end'])
                )):
                    result.append(post)
                    break

        print('time: ', time.time() - start_time)
        return Response(result)

    @staticmethod
    def remove_accents(text):
        text = str(text)
        text = unicodedata.normalize('NFD', text)
        text = re.sub(r'[\u0300-\u036f]', '', text)
        return text.lower()

    @staticmethod
    def search_in_profile(text, post):
        user = post['parent_id']
        parent = ParentProfile.objects.get(user=user)
        return SearchView.remove_accents(text) in SearchView.remove_accents(parent.parentname)

    @staticmethod
    def search_in_weekday(text, post):
        for class_time in post['class_times']:
            weekday = class_time['weekday']
            weekday = Weekday.map_value_to_display(weekday)
            if SearchView.remove_accents(text) in SearchView.remove_accents(weekday):
                return True
        return False
    
