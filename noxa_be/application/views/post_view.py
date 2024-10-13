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


"""
PostView API endpoint for JobPost model. Use for parent to CRUD their job posts.
"""

class PostView(APIView):
    permission_classes = [IsAuthenticated, IsParent]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes] 
    
    def get(self, request, pk=None):
        if pk:
            if User.objects.filter(user_id=pk).exists():
                user = get_object_or_404(User, user_id=pk)
                posts = JobPost.objects.filter(parent_id=user)
                post_serializer = PostSerializer(posts, many=True, context={'request_type': 'detail'})
            else:
                post = get_object_or_404(JobPost, post_id=pk)
                job_registerd = JobRegister.objects.filter(post_id=post)
                registration_serializer = JobRegistrationSerializer(job_registerd, many=True)
                return Response(registration_serializer.data)
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
    
# class PostView(APIView):
#     def get_permissions(self):
#         if self.request.method == 'GET':
#             return [AllowAny()]  # Không yêu cầu xác thực cho GET
#         return [permission() for permission in self.permission_classes] 

#     def get(self, request, pk=None):
#         filters = {key: request.query_params.get(key) for key in ['subject', 'status', 'grade', 'background_desired'] if request.query_params.get(key) is not None}

#         if pk:
#             post = get_object_or_404(JobPost, post_id=pk)
#             serializer = PostSerializer(post)
#         else:
#             posts = JobPost.objects.filter(**filters)
#             serializer = PostSerializer(posts, many=True)
        
#         return Response(serializer.data)
    
class PostSearchView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes]
    
    
    def get(self, request):
        query = request.query_params.get('query', None)
        filters = {key: request.query_params.get(key) for key in ['subject', 'status', 'grade', 'background_desired'] if request.query_params.get(key) is not None}
        posts = JobPost.objects.all()

        if query:
            posts = JobPost.objects.filter(
                Q(subject__icontains=query) |
                Q(status__icontains=query) |
                Q(grade__icontains=query) | 
                Q(background_desired__icontains=query) |
                Q(duration__icontains=query) | 
                Q(session_per_week__icontains=query) |
                Q(wage_per_hour__icontains=query) | 
                Q(student_number__icontains=query)
            )

        if filters:
            posts = posts.filter(**filters)


        serializer = PostSerializer(posts, many=True)
        
        return Response(serializer.data)


        
    
