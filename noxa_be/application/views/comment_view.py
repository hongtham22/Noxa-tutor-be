from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from application.models import *
from accounts.models import *
from application.serializers.comment_serializer import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class JobPostCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Cho phép mọi người truy cập GET, nhưng yêu cầu xác thực cho các phương thức khác
        if self.request.method == "GET":
            return [AllowAny()]

        return [permission() for permission in self.permission_classes]
    
    def get(self, request, pk):
        # kiểm tra xem pk là post_id hay comment_id
        if JobPost.objects.filter(post_id=pk).exists():
            post = get_object_or_404(JobPost, post_id=pk)
            comments = JobPostComment.objects.filter(post_id=post, comment_parent_id=None).order_by('-created_at')
            comment_serializer = CommentSerializer(comments, many=True, context={'request': request})
            total_comments = JobPostComment.objects.filter(post_id=post).count()
            return Response({'total_comments': total_comments, 'comments': comment_serializer.data})
        elif JobPostComment.objects.filter(comment_id=pk).exists():
            comment = get_object_or_404(JobPostComment, comment_id=pk)
            comments = JobPostComment.objects.filter(comment_parent_id=comment).order_by('created_at')
            comment_serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response({'total_comments': len(comments), 'comments': comment_serializer.data})
        else:
            return Response({'message': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        data = request.data
        comment_serializer = CommentSerializer(data=data, context={'request': request})
        if comment_serializer.is_valid():
            comment_serializer.save()
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)