from rest_framework import serializers
from accounts.models import User, TutorProfile, ParentProfile, JobPost, TutorClasses, Feedback, Notification, TutorSubject, ClassTime

from accounts.enums import *

class FeedbackSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    parent_avt = serializers.SerializerMethodField()
    total_feedback = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

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
            'created_at': {'read_only': True},
            'parent_name': {'read_only': True},
            'parent_avt': {'read_only': True},
            'total_feedback': {'read_only': True},
            'average_rating': {'read_only': True},
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
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        tutor_id = instance.tutor_id.user.user_id
        parent_id = instance.parent_id.user.user_id

        representation['tutor_id'] = str(tutor_id)
        representation['parent_id'] = str(parent_id)

        # Conditionally include average_rating
        if self.context.get('include_average_rating') == True:
            representation['average_rating'] = self.get_average_rating(instance)
        else :
            representation.pop('average_rating', None)

        return representation
    
    def create(self, validated_data):
        feedback = Feedback.objects.create(**validated_data)
        return feedback
    
    def get_parent_name(self, obj):
        parent = obj.parent_id
        return parent.parentname
    
    def get_parent_avt(self, obj):
        parent = obj.parent_id
        
        if parent.avatar:
            return parent.avatar.url
        return None
    
    def get_total_feedback(self, obj):
        tutor_id = obj.tutor_id.user
        
        feedbacks = Feedback.objects.filter(tutor_id__user=tutor_id)
        return feedbacks.count()
    
    def get_average_rating(self, obj):
        tutor_id = obj.tutor_id.user
        
        feedbacks = Feedback.objects.filter(tutor_id__user=tutor_id)
        total = 0
        for feedback in feedbacks:
            total += feedback.rating
        if feedbacks.count() == 0:
            return 0
        return total / feedbacks.count()