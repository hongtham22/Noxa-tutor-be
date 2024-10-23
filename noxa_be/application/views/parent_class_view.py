from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accounts.permission import IsParent
from application.serializers.class_serializer import ClassSerializer
from application.serializers.feedback_serializer import FeedbackSerializer



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

    def post(self, request):
        feedback_serializer = FeedbackSerializer(data=request.data)
        if feedback_serializer.is_valid():
            feedback_serializer.save()
            return Response(feedback_serializer.data, status=status.HTTP_201_CREATED)
        return Response(feedback_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 