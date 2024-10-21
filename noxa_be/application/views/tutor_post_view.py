from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsTutor
from accounts.models import JobRegister, User
from application.serializers.job_registration_serializer import JobRegistrationSerializer

from .helper import PostHelper


class TutorPostView(APIView):
    helper = PostHelper()
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            if User.objects.filter(user_id=pk).exists():
                posts = self.helper.get_posts_by_user_id(pk)
            else:
                post_serializer = self.get_posts_by_post_id(pk)
                return Response(post_serializer.data)
        else:
            status = request.query_params.get('status', 'approved')
            if status == 'registered':
                user_id = request.user.user_id
                posts = self.helper.get_registered_posts(user_id)
            else:
                posts = self.helper.get_posts_by_status(request, status)
        return self.helper.paginate_posts(posts, request)
    
    def post(self, request):
        registration = JobRegistrationSerializer(data=request.data)
        if registration.is_valid():
            registration.save()
            return Response(registration.data, status=status.HTTP_201_CREATED)
        return Response(registration.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        registration = get_object_or_404(JobRegister, registation_id=pk)
        registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

