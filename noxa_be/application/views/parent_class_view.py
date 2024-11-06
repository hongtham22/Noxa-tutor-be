from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from accounts.permission import IsParent
from application.serializers.class_serializer import ClassSerializer
from application.serializers.feedback_serializer import FeedbackSerializer
from accounts.models import Feedback



class AppointView(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def post(self, request):
        appointment_serializer = ClassSerializer(data=request.data)
        if appointment_serializer.is_valid():
            appointment_serializer.save()
            return Response(appointment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(appointment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FeedbackView(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get(self, request, id=None):
        if id:
            print ('id: ', id)
            feedback = Feedback.objects.filter(feedback_id=id).first()
            if feedback:
                feedback_serializer = FeedbackSerializer(feedback)
                return Response(feedback_serializer.data)
            feedbacks = Feedback.objects.filter(tutor_id__user__user_id=id)
            feedbacks_serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(feedbacks_serializer.data)
        feedbacks = Feedback.objects.all()
        feedbacks_serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(feedbacks_serializer.data)

    def post(self, request):
        feedback_serializer = FeedbackSerializer(data=request.data)
        if feedback_serializer.is_valid():
            feedback_serializer.save()
            return Response(feedback_serializer.data, status=status.HTTP_201_CREATED)
        print(feedback_serializer)
        return Response(feedback_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 