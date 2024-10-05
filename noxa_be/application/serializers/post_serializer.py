from rest_framework import serializers
from accounts.models import User, TutorProfile, ParentProfile, JobPost, TutorClasses, Feedback, Notification, TutorSubject, ClassTime

from accounts.enums import *


class ClassTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTime
        fields = ['weekday', 'time_start', 'time_end']
        extra_kwargs = {
            'weekday': {'required': True},
            'time_start': {'required': True},
            'time_end': {'required': True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['weekday']:
            representation['weekday'] = Weekday.map_value_to_display(representation['weekday'])

        return representation
    
    def to_internal_value(self, data):
        weekday = data.get('weekday')
        if weekday:
            data['weekday'] = Weekday.map_display_to_value(weekday)

        return data
    
    def create(self, validated_data):
        class_time = ClassTime.objects.create(**validated_data)
        return class_time

    def update(self, instance, validated_data):
        pass

class PostSerializer(serializers.ModelSerializer):
    class_times = ClassTimeSerializer(many=True, required=True)

    class Meta:
        model = JobPost
        fields = '__all__'
        extra_kwargs = {
            'post_id': {'read_only': True},
            'created_at': {'read_only': True},
            'last_updated': {'read_only': True},
            'status': {'read_only': True},
            'subject': {'required': True},
            'address': {'required': True},
            'grade': {'required': True},
            'session_per_week': {'required': True},
            'wage_per_session': {'required': True},
            'student_number': {'required': True},
            'background_desired': {'required': False},
            'duration': {'required': False},
            'description': {'required': False},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['subject']:
            representation['subject'] = Subject.map_value_to_display(representation['subject'])

        if representation['background_desired']:
            representation['background_desired'] = EducationalBackground.map_value_to_display(representation['background_desired'])

        request_type = self.context.get('request_type')
        if request_type == 'list':
            representation.pop('class_times')
            representation.pop('description')
            representation.pop('duration')
            representation.pop('created_at')
            representation.pop('last_updated')
            representation.pop('background_desired')

        return representation

    def to_internal_value(self, data):
        subject = data.get('subject')
        if subject:
            data['subject'] = Subject.map_display_to_value(str(subject))

        background_desired = data.get('background_desired')
        if background_desired:
            data['background_desired'] = EducationalBackground.map_display_to_value(background_desired)

        parent_id = data.get('parent_id')
        if parent_id:
            user = User.objects.get(user_id=parent_id)
            data['parent_id'] = user

        return data

    def create(self, validated_data):
        class_times_data = validated_data.pop('class_times')
        post = JobPost.objects.create(**validated_data)
        for class_time_data in class_times_data:
            class_serializer = ClassTimeSerializer(data=class_time_data)
            if class_serializer.is_valid():
                class_serializer.save(post_id=post)

        return post

    def update(self, instance, validated_data):
        pass
