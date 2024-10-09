import json
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.db.models import Q
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsAdmin
from accounts.models import *
from accounts.enums import *
from application.serializers.post_serializer import PostSerializer 

"""
AdminPostView API endpoint for JobPost model. Use for admin to view all job posts and change their status.

- CustomPagination: Custom pagination class for JobPost model.

- GET: get all job posts with status filter. If pk is provided, get job posts by user_id or post_id. If nothing provided, return all pending job posts.
- POST: change status of a job post by post_id. Add notification to both user and database.

"""

class CustomPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100  

class AdminPostView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get (self, request, pk=None):
        if pk:
            if User.objects.filter(user_id=pk).exists():
                post_serializer = self.get_posts_by_user_id(pk)
            else:
                post_serializer = self.get_posts_by_post_id(pk)
            return Response(post_serializer.data)
        else:
            status = request.query_params.get('status', 'pending')
            posts = self.get_posts_by_status(request, status)
            paginator = CustomPagination()
            paginated_posts = paginator.paginate_queryset(posts, request)
            post_serializer = PostSerializer(paginated_posts, many=True, context={'request_type': 'detail'})
            return paginator.get_paginated_response(post_serializer.data)
            
    def post (self, request):
        post_id = request.data.get('post_id')
        post_status = request.data.get('status')
        post_status = Status.map_display_to_value(post_status)
        post = JobPost.objects.get(post_id=post_id)
        post.status = post_status
        post.save()

        self.add_notification(post)
        return Response(status=status.HTTP_200_OK)
    
    def get_posts_by_user_id(self, user_id):
        status = Status.PENDING_APPROVAL
        user = get_object_or_404(User, user_id=user_id)
        posts = JobPost.objects.filter(parent_id=user, status=status).order_by('-created_at')
        post_serializer = PostSerializer(posts, many=True, context={'request_type': 'detail'})
        return post_serializer
    
    def get_posts_by_post_id(self, post_id):
        post = get_object_or_404(JobPost, post_id=post_id)
        post_serializer = PostSerializer(post, context={'request_type': 'detail'})
        return post_serializer
    
    def get_posts_by_status(self, request, status):
        
        if status == 'approved':
            status = Status.APPROVED
        elif status == 'pending':
            status = Status.PENDING_APPROVAL
        elif status == 'rejected':
            status = Status.REJECTED
        elif status == 'closed':
            status = Status.CLOSED

        posts = JobPost.objects.filter(status=status).order_by('-created_at')
        return posts
    
    def add_notification(self, post):
        parent_id = post.parent_id.user_id

        notification = Notification()
        notification.user_id = post.parent_id
        notification.description = 'Your post has been {}'.format(post.status)
        notification.read = False 
        notification.save()

        active_connections = cache.get('active_connections', {})

        message = json.dumps({
            'message': 'Your post has been {}'.format(post.status),
            'time': notification.created_at.strftime('%d/%m/%Y , %H:%M:%S'),
        })
            
        if str(parent_id) in active_connections:
            active_connections[str(parent_id)].append(message)

        cache.set('active_connections', active_connections)