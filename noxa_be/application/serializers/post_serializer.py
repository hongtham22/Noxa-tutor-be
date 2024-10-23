from rest_framework import serializers
from accounts.models import User, TutorProfile, ParentProfile, JobPost, TutorClasses, Feedback, Notification, TutorSubject, ClassTime

from accounts.enums import *


class ClassTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTime
        fields = ['id', 'weekday', 'time_start', 'time_end']
        extra_kwargs = {
            'class_id': {'read_only': True},
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
    class_times = ClassTimeSerializer(many=True, required=False)
    username = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    class Meta:
        model = JobPost
        fields = '__all__'
        extra_kwargs = {
            'post_id': {'read_only': True},
            'username': {'read_only': True},
            'parent_name': {'read_only': True},
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
            'avatar': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['subject']:
            representation['subject'] = Subject.map_value_to_display(representation['subject'])

        if representation['background_desired']:
            representation['background_desired'] = EducationalBackground.map_value_to_display(representation['background_desired'])

        if representation['status']:
            representation['status'] = Status.map_value_to_display(representation['status'])

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
        if instance.status == Status.CLOSED:
            raise serializers.ValidationError("This post has been appointed to another tutor and closed")
        class_times_data = validated_data.pop('class_times')
        instance.subject = validated_data.get('subject', instance.subject)
        instance.address = validated_data.get('address', instance.address)
        instance.grade = validated_data.get('grade', instance.grade)
        instance.session_per_week = validated_data.get('session_per_week', instance.session_per_week)
        instance.wage_per_session = validated_data.get('wage_per_session', instance.wage_per_session)
        instance.student_number = validated_data.get('student_number', instance.student_number)
        instance.background_desired = validated_data.get('background_desired', instance.background_desired)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.description = validated_data.get('description', instance.description)
        instance.status = Status.PENDING_APPROVAL
        instance.save()

        class_times = ClassTime.objects.filter(post_id=instance)
        for class_time in class_times:
            class_time.delete()
        
        for class_time_data in class_times_data:
            class_time_data['weekday'] = Weekday.map_display_to_value(class_time_data.get('weekday'))
            class_time = ClassTime.objects.create(**class_time_data, post_id=instance)

        return instance

    def get_parent_name(self, obj):
        parent = ParentProfile.objects.get(user=obj.parent_id)
        return parent.parentname
    
    def get_username(self, obj):
        username = obj.parent_id.username
        return username
    
    def get_avatar(self, obj):
        try:
            parent = ParentProfile.objects.get(user=obj.parent_id)
            if parent.avatar:
                return parent.avatar.url
            else:
                return 'No avatar'
        except:
            return 'No avatar'