from django.shortcuts import render, get_object_or_404
from accounts.models import JobPost
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers.jobPost_serializer import JobPostSerializer  
from django.db.models import Q

class PostView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Không yêu cầu xác thực cho GET
        return [permission() for permission in self.permission_classes] 

    def get(self, request, pk=None):
        filters = {key: request.query_params.get(key) for key in ['subject', 'status', 'grade', 'background_desired'] if request.query_params.get(key) is not None}

        if pk:
            post = get_object_or_404(JobPost, post_id=pk)
            serializer = JobPostSerializer(post)
        else:
            posts = JobPost.objects.filter(**filters)
            serializer = JobPostSerializer(posts, many=True)
        
        return Response(serializer.data)
    
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


        serializer = JobPostSerializer(posts, many=True)
        
        return Response(serializer.data)