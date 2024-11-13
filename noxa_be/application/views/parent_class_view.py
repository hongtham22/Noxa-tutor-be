from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.utils.serializer_helpers import ReturnList

from accounts.permission import IsParent
from application.serializers.class_serializer import ClassSerializer
from application.serializers.feedback_serializer import FeedbackSerializer
from accounts.models import Feedback, ParentProfile, User
from notifications.notification_service import NotificationService, ParentProfile


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
                feedbacks_serializer = FeedbackSerializer(feedback)

            else :
                feedbacks = Feedback.objects.filter(tutor_id__user__user_id=id)
                feedbacks_serializer = FeedbackSerializer(feedbacks, many=True, context={'include_average_rating': False})
            feedbacks = {}
            feedbacks['feedbacks'] = feedbacks_serializer.data
            # if feedbacks_serializer.data is not a OrderedDict, don't include average_rating
            if type(feedbacks_serializer.data) == ReturnList:
                feedbacks['average_rating'] = self.get_average_rating(feedbacks_serializer.data)

            return Response(feedbacks)
        feedbacks = Feedback.objects.all()
        feedbacks_serializer = FeedbackSerializer(feedbacks, many=True, context={'include_average_rating': True})
        return Response(feedbacks_serializer.data)

    def post(self, request):
        feedback_serializer = FeedbackSerializer(data=request.data)
        if feedback_serializer.is_valid():
            feedback_serializer.save()

            parent = ParentProfile.objects.filter(user__user_id=request.data['parent_id']).first()

            parent_name = parent.parentname if parent.parentname != "" else parent.user.username
            message = f'You have received a feedback from {parent_name}'
            parent_avatar = parent.avatar.url if parent.avatar else None
            additional_information = {
                'parent_id': str(parent.user.user_id),
                'parent_avatar': parent_avatar
            }

            NotificationService.add_notification(User.objects.filter(user_id=feedback_serializer.data['tutor_id']).first(), message)
            return Response(feedback_serializer.data, status=status.HTTP_201_CREATED)
        return Response(feedback_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    def get_average_rating(self, feedbacks):
        total = 0
        for feedback in feedbacks:
            total += feedback['rating']
        if len(feedbacks) == 0:
            return 0
        return total / len(feedbacks)