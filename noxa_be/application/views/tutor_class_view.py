from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permission import IsTutor
from accounts.models import TutorClasses
from application.serializers.class_serializer import ClassSerializer
from application.serializers.post_serializer import PostSerializer

from .helper import PostHelper


class TutorClassView(APIView):
    helper = PostHelper()
    permission_classes = [IsTutor]

    def get (self, request):
        status = request.query_params.get('status', 'registered')
        user_id = request.user.user_id
        if not user_id:
            return Response(status=404)
        if status == 'registered':
            posts = self.helper.get_registered_posts(user_id)
            posts_serializer = PostSerializer(posts, many=True)
            return Response(posts_serializer.data)
        elif status == 'appointed':
            classes = TutorClasses.objects.filter(tutor_id__user_id=user_id)
            class_serializer = ClassSerializer(classes, many=True)
            return Response(class_serializer.data)