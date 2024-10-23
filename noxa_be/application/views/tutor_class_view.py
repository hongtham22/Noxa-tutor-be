from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permission import IsTutor
from application.models import TutorClasses
from application.serializers.class_serializer import ClassSerializer

from .helper import PostHelper


class TutorClassView(APIView):
    helper = PostHelper()
    permission_classes = [IsTutor]

    def get (self, request):
        user_id = request.user.user_id
        classes = TutorClasses.objects.filter(tutor_id__user_id=user_id)
        class_serializer = ClassSerializer(classes, many=True)
        return Response(class_serializer.data)