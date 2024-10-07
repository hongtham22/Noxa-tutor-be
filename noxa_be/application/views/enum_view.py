from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.enums import *


class EnumView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        background_enum = EducationalBackground.get_choices_display()
        subject_enum = Subject.get_choices_display()
        status_enum = Status.get_choices_display()
        return Response({'background_enum': background_enum, 'subject_enum': subject_enum, 'status_enum': status_enum})