from rest_framework import serializers
from accounts.models import *
from application.models import *

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    comment_children_count = serializers.SerializerMethodField()
    is_my_comment = serializers.SerializerMethodField()

    class Meta:
        model = JobPostComment
        fields = [
            'comment_id',
            'post_id',
            'user_id',
            'comment_parent_id',
            'comment',
            'created_at',
            'user',
            'comment_children_count', 
            'is_my_comment',
        ]
        extra_kwargs = {
            'comment_id': {'read_only': True},
            'created_at': {'read_only': True},
            'user': {'required': False},
            'comment_children_count': {'required': False},
            'is_my_comment': {'required': False},
        }
    
    def create(self, validated_data):
        return super().create(validated_data)

    def get_user(self, obj):
        user_role = obj.user_id.role
        if user_role == 'Tutor':
            try:
                tutor = TutorProfile.objects.get(user_id=obj.user_id)
                return {
                    'id': str(obj.user_id.user_id),
                    'name': tutor.tutorname,
                    'avatar': tutor.avatar.url if tutor.avatar else None
                }
            except:
                return {
                    'id': str(obj.user_id.user_id),
                    'name': obj.user_id.username,
                    'avatar': None
                }
        else:
            try:
                parent = ParentProfile.objects.get(user_id=obj.user_id)
                return {
                    'id': str(obj.user_id.user_id),
                    'name': parent.parentname,
                    'avatar': parent.avatar.url if parent.avatar else None

                }
            except:
                return {
                    'id': str(obj.user_id.user_id),
                    'name': obj.user_id.username,
                    'avatar': None
                }
    
    def get_comment_children_count(self, obj):
        return JobPostComment.objects.filter(comment_parent_id=obj.comment_id).count()
    
    def get_is_my_comment(self, obj):
        user = self.context['request'].user
        return obj.user_id == user