from rest_framework import serializers
from accounts.models import *
from accounts.enums import *

class ReportSerializer(serializers.ModelSerializer):
    reported_name = serializers.SerializerMethodField()
    reportee_name = serializers.SerializerMethodField()
    reported_avt = serializers.SerializerMethodField()
    reportee_avt = serializers.SerializerMethodField()
    class Meta:
        model = Report
        fields = '__all__'
        extra_kwargs = {
            'report_id': {'read_only': True},
            'post': {'required': False},
            'feedback_id': {'required': False},
            'reported': {'required': True},
            'reportee': {'required': True},
            'description': {'required': True},
            'report_type': {'required': True},
            'created_at': {'read_only': True},
            'reported_name': {'read_only': True},
            'reportee_name': {'read_only': True},
            'reported_avt': {'read_only': True},
            'reportee_avt': {'read_only': True}
        }

    def to_internal_value(self, data):
        data = data.copy()

        post = data.get('post_id', None)
        feedback = data.get('feedback_id', None)
        reported = data.get('reporter_id', None)
        reportee = data.get('reported_party_id', None)  
        report_type = data.get('type', None)

        if not reported or not reportee:
            raise serializers.ValidationError("Reporter ID or Reported Party ID is required")

        if not post and not feedback:
            raise serializers.ValidationError("Post ID or Feedback ID is required")
        
        if not report_type:
            raise serializers.ValidationError("Report type is required")

        reported = User.objects.filter(user_id=reported).first()
        if not reported:
            raise serializers.ValidationError("Reporter does not exist")
        
        reportee = User.objects.filter(user_id=reportee).first()
        if not reportee:
            raise serializers.ValidationError("Reported party does not exist")
        
        if post:
            post = JobPost.objects.filter(post_id=post).first()

            if not post:
                raise serializers.ValidationError("Post does not exist")
            if post.status == Status.CLOSED:
                raise serializers.ValidationError("Post has been closed")
            
        if feedback:
            feedback = Feedback.objects.filter(feedback_id=feedback).first()
            if not feedback:
                raise serializers.ValidationError("Feedback does not exist")
        
        report_type = ReportType.map_display_to_value(report_type)
            
        data.pop('reporter_id')
        data.pop('reported_party_id')
        data.pop('type')
        data['reported'] = reported
        data['reportee'] = reportee
        data['post'] = post
        data['feedback'] = feedback
        data['report_type'] = report_type

        return data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reporter_id'] = instance.reported.user_id
        representation['reported_party_id'] = instance.reportee.user_id
        representation['type'] = ReportType.map_value_to_display(instance.report_type)
        representation['post_id'] = instance.post.post_id if instance.post else None
        representation['feedback_id'] = instance.feedback.feedback_id if instance.feedback else None
        representation['reporter_name'] = representation['reported_name']
        representation['reported_party_name'] = representation['reportee_name']
        representation['reporter_avt'] = representation['reported_avt']
        representation['reported_party_avt'] = representation['reportee_avt']
        representation.pop('reported')
        representation.pop('reportee')
        representation.pop('report_type')
        representation.pop('post')
        representation.pop('feedback')
        representation.pop('reported_name')
        representation.pop('reportee_name')
        representation.pop('reported_avt')
        representation.pop('reportee_avt')
        return representation
    
    def create(self, validated_data):
        # check if the report is already exist
        reported = validated_data.get('reported')
        reportee = validated_data.get('reportee')
        post = validated_data.get('post')
        feedback = validated_data.get('feedback')
        
        if post or feedback:
            if post:
                report = Report.objects.filter(reported=reported, reportee=reportee, post=post).first()
            else:
                report = Report.objects.filter(reported=reported, reportee=reportee, feedback=feedback).first()
            if report:
                raise serializers.ValidationError("This report is already exist")

        report = Report.objects.create(**validated_data)
        return report

    def get_reported_name(self, obj):
        user = obj.reported
        name = user.username

        reported_user = TutorProfile.objects.filter(user=user).first()
        if not reported_user:
            reported_user = ParentProfile.objects.filter(user=user).first()
            if not reported_user.parentname:
                return name
            name = reported_user.parentname
        else:
            if not reported_user.tutorname:
                return name
            name = reported_user.tutorname
        return name
    
    def get_reportee_name(self, obj):
        user = obj.reportee
        name = user.username
        reportee_user = TutorProfile.objects.filter(user=user).first()
        if not reportee_user:
            reportee_user = ParentProfile.objects.filter(user=user).first()
            if not reportee_user.parentname:
                return name
            name = reportee_user.parentname
        else:
            if not reportee_user.tutorname:
                return name
            name = reportee_user.tutorname
        return name
    
    def get_reported_avt(self, obj):
        user = obj.reported
        
        reported_user = TutorProfile.objects.filter(user=user).first()
        if not reported_user:
            reported_user = ParentProfile.objects.filter(user=user).first()
            if not reported_user.avatar:
                return None
            return reported_user.avatar.url
        else:
            if not reported_user.avatar:
                return None
            return reported_user.avatar.url
        
    def get_reportee_avt(self, obj):
        user = obj.reportee
        
        reportee_user = TutorProfile.objects.filter(user=user).first()
        if not reportee_user:
            reportee_user = ParentProfile.objects.filter(user=user).first()
            if not reportee_user.avatar:
                return None
            return reportee_user.avatar.url
        else:
            if not reportee_user.avatar:
                return None
            return reportee_user.avatar.url
        

