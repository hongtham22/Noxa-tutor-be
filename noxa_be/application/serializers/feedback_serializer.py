from rest_framework import serializers
from accounts.models import User, TutorProfile, ParentProfile, JobPost, TutorClasses, Feedback, Notification, TutorSubject, ClassTime

from accounts.enums import *

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        extra_kwargs = {
            'feedback_id': {'read_only': True},
            'class_id': {'required': True},
            'parent_id': {'required': True},
            'tutor_id': {'required': True},
            'rating': {'required': True},
            'description': {'required': False},
        }

    def to_internal_value(self, data):
        data = data.copy()
        
        class_id = data.get('class_id')
        parent_id = data.get('parent_id')
        tutor_id = data.get('tutor_id')
        
        if not class_id:
            raise serializers.ValidationError("Class ID is required")
        if not parent_id:
            raise serializers.ValidationError("Parent ID is required")
        if not tutor_id:
            raise serializers.ValidationError("Tutor ID is required")
        
        tutor_class = TutorClasses.objects.filter(class_id=class_id).first()
        if not tutor_class:
            raise serializers.ValidationError("Class of this tutor does not exist")
        
        parent_profile = ParentProfile.objects.filter(user__user_id=parent_id).first()
        if not parent_profile:
            raise serializers.ValidationError("Parent does not exist")
        
        tutor_profile = TutorProfile.objects.filter(user__user_id=tutor_id).first()
        if not tutor_profile:
            raise serializers.ValidationError("Tutor does not exist")
        
        data['class_id'] = tutor_class
        data['parent_id'] = parent_profile
        data['tutor_id'] = tutor_profile
        return data
    
    def create(self, validated_data):
        feedback = Feedback.objects.create(**validated_data)
        return feedback
