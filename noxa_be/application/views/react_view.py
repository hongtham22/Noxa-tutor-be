from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from application.models import *
from accounts.models import *
from application.serializers.comment_serializer import *
from application.serializers.react_serialier import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class JobPostReactView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Cho phép mọi người truy cập GET, nhưng yêu cầu xác thực cho các phương thức khác
        if self.request.method == "GET":
            return [AllowAny()]

        return [permission() for permission in self.permission_classes]
    
    def get(self, request, pk):
        post = get_object_or_404(JobPost, post_id=pk)
        reactions = JobPostReact.objects.filter(post_id=post)
        react_serializer = ReactSerializer(reactions, many=True)
        return Response(react_serializer.data)
        
        
    def post(self, request, pk):
        post = get_object_or_404(JobPost, post_id=pk)
        reaction, created = JobPostReact.objects.get_or_create(
            post_id=post, user_id=request.user, defaults={"reaction_type": 1}
        )

        if not created:
            reaction.delete()
            return Response({"detail": "Unliked"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Liked"}, status=status.HTTP_201_CREATED)