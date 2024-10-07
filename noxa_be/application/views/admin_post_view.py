from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsAdmin
from accounts.models import *
from accounts.enums import *
from application.serializers.post_serializer import PostSerializer 

class CustomPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100  

class AdminPostView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get (self, request, pk=None):
        if pk:
            post = get_object_or_404(JobPost, post_id=pk)
            post_serializer = PostSerializer(post, context={'request_type': 'detail'})
            return Response(post_serializer.data)
        else:
            status = Status.PENDING_APPROVAL
            posts = JobPost.objects.filter(status=status).order_by('-created_at')
            paginator = CustomPagination()
            paginated_posts = paginator.paginate_queryset(posts, request)

            post_serializer = PostSerializer(paginated_posts, many=True, context={'request_type': 'detail'})
            
            # Trả về kết quả phân trang
            return paginator.get_paginated_response(post_serializer.data)
        
    def post (self, request):
        post_id = request.data.get('post_id')
        post_status = request.data.get('status')
        post_status = Status.map_display_to_value(post_status)
        post = JobPost.objects.get(post_id=post_id)
        post.status = post_status
        post.save()
        return Response(status=status.HTTP_200_OK)

