from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permission import IsAdmin, IsTutorOrParent
from application.serializers.report_serializer import ReportSerializer
from accounts.models import Report, User
from notifications.notification_service import NotificationService
from accounts.enums import Role
from application.models import JobPostComment

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
            reports = Report.objects.filter(report_id=pk).first()

            if reported:
                reports = Report.objects.filter(reported=reported, resolved=False)
            if reportee:
                reports = Report.objects.filter(reportee=reportee, resolved=False)
            if reports:
                serializer = ReportSerializer(reports, many=True)
                data = serializer.data
                for report in data:
                    if report['type'] == 'Bình luận':
                        comment = JobPostComment.objects.filter(comment_id=report['comment_id']).first()
                        comment_parent_id = comment.comment_parent_id
                        if comment_parent_id:    
                            comment_parent = JobPostComment.objects.filter(comment_id=comment_parent_id.comment_id).first()
                            comments =  [str(comment_parent.comment_id), str(comment.comment_id)]
                        else:
                            comments = [str(comment.comment_id)]
                        report['comments'] = comments
                        report['reported_comment'] = comment.comment
                return Response(data)
        else:
            reports = Report.objects.filter(resolved=False).order_by('-created_at')
            serializer = ReportSerializer(reports, many=True)
            for report in serializer.data:
                if report['type'] == 'Bình luận':
                    comment = JobPostComment.objects.filter(comment_id=report['comment_id']).first()
                    comment_parent_id = comment.comment_parent_id
                    if comment_parent_id:    
                        comment_parent = JobPostComment.objects.filter(comment_id=comment_parent_id.comment_id).first()
                        comments =  [str(comment_parent.comment_id), str(comment.comment_id)]
                    else:
                        comments = [str(comment.comment_id)]
                    report['comments'] = comments
                    report['reported_comment'] = comment.comment
            return Response(serializer.data)
        
    def post(self, request):
        try: 
            report = ReportSerializer(data=request.data)
            if report.is_valid():
                report.save()
                if report.data['type'] == 'Bình luận':
                    data = report.data
                    comments = None
                    
                    comment = JobPostComment.objects.filter(comment_id=report.data['comment_id']).first()
                    comment_parent_id = comment.comment_parent_id
                    if comment_parent_id:    
                        comment_parent = JobPostComment.objects.filter(comment_id=comment_parent_id.comment_id).first()
                        comments = [str(comment_parent.comment_id), str(comment.comment_id)]
                    else:
                        comments = [str(comment.comment_id)]

                    data['comments'] = comments
                    data['reported_comment'] = comment.comment
                    
                
                    admins = User.objects.filter(role=Role.ADMIN)
                    for admin in admins:
                        message = f'{report.data["reporter_name"]} has reported user {report.data["reported_party_name"]}'
                        reporter = report.data['reporter_name']
                        reporter_id = report.data['reporter_id']
                        reporter_avatar = report.data['reporter_avt']
                        addtional_information = {
                            'reporter': str(reporter),
                            'reporter_id': str(reporter_id),
                            'reporter_avatar': reporter_avatar,
                            'report_id': str(report.data['report_id'])
                        }
                        
                        if report.data['type'] == 'Bình luận':
                            addtional_information['comments'] = comments
                        NotificationService.add_notification(admin, message, addtional_information)

                    return Response(data, status=status.HTTP_201_CREATED)
                return Response(report.data, status=status.HTTP_201_CREATED)
            return Response(report.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        report = Report.objects.filter(report_id=request.data.get('report_id')).first()
        report.resolved = True

        report.save()
        return Response(status=status.HTTP_200_OK)