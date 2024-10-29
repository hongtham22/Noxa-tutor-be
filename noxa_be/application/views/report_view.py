from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsAdmin, IsTutorOrParent
from application.serializers.report_serializer import ReportSerializer
from accounts.models import Report, User

class ReportView(APIView):
    permisson_classes = [IsAuthenticated, IsTutorOrParent]

    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAdmin()] 
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [permission() for permission in self.permission_classes] 

    def get(self, request, pk=None):
        if pk:
            reported = User.objects.filter(user_id=pk).first()
            reportee = User.objects.filter(user_id=pk).first()
            report = Report.objects.filter(report_id=pk).first()
            if reported:
                reports = Report.objects.filter(reported=reported, resolved=False)
                serializer = ReportSerializer(reports, many=True)
                return Response(serializer.data)
            if reportee:
                reports = Report.objects.filter(reportee=reportee, resolved=False)
                serializer = ReportSerializer(reports, many=True)
                return Response(serializer.data)
            if report:
                serializer = ReportSerializer(report)
                return Response(serializer.data)
        else:
            reports = Report.objects.filter(resolved=False).order_by('-created_at')
            serializer = ReportSerializer(reports, many=True)
            return Response(serializer.data)
        
    def post(self, request):
        report = ReportSerializer(data=request.data)
        if report.is_valid():
            report.save()
            return Response(report.data, status=status.HTTP_201_CREATED)
        print (report)
        return Response(report.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        report = Report.objects.filter(report_id=request.data.get('report_id')).first()
        report.resolved = True

        report.save()
        return Response(status=status.HTTP_200_OK)