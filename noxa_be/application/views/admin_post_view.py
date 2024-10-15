import json
from django.db.models import Q
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsAdmin
from accounts.models import *
from accounts.enums import *
from application.serializers.post_serializer import PostSerializer 

from .helper import PostHelper

"""
AdminPostView API endpoint for JobPost model. Use for admin to view all job posts and change their status.

- CustomPagination: Custom pagination class for JobPost model.

- GET: get all job posts with status filter. If pk is provided, get job posts by user_id or post_id. If nothing provided, return all pending job posts.
- POST: change status of a job post by post_id. Add notification to both user and database.

"""

class AdminPostView(APIView):
    helper = PostHelper()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get (self, request, pk=None):
        if pk:
            if User.objects.filter(user_id=pk).exists():
                posts = self.helper.get_posts_by_user_id(pk)
            else:
                post_serializer = self.helper.get_posts_by_post_id(pk)
                return Response(post_serializer.data)
        else:
            status = request.query_params.get('status', 'pending')
            posts = self.helper.get_posts_by_status(request, status)
        return self.helper.paginate_posts(posts, request)
            
    def post (self, request):
        post_id = request.data.get('post_id')
        post_status = request.data.get('status')
        post_status = Status.map_display_to_value(post_status)
        post = JobPost.objects.get(post_id=post_id)
        post.status = post_status
        post.save()

        self.add_notification(post)
        return Response(status=status.HTTP_200_OK)
        
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