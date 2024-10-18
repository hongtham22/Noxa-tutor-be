from rest_framework import serializers
from accounts.models import User, TutorProfile, ParentProfile, JobPost, TutorClasses, Feedback, Notification, TutorSubject, ClassTime

from accounts.enums import *

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorClasses
        fields = '__all__'
        extra_kwargs = {
            'class_id': {'read_only': True},
            'created_at': {'read_only': True},
            'finished': {'required': False},
            'tutor_id': {'required': True},
            'post_id': {'required': True}
        }

    def to_internal_value(self, data):
        data = data.copy()
        
        tutor_id = data.get('tutor_id')
        post_id = data.get('post_id')
       
        if not tutor_id:
            raise serializers.ValidationError("Tutor ID is required")
        if not post_id:
            raise serializers.ValidationError("Post ID is required")
        
        user = User.objects.filter(user_id=tutor_id).first()
        tutor_profile = TutorProfile.objects.filter(user=user).first()
        if not tutor_profile:
            raise serializers.ValidationError("Tutor does not exist")
        
        job_post = JobPost.objects.filter(post_id=post_id).first()
        if not job_post:
            raise serializers.ValidationError("Job post does not exist")
        
        post_exist = TutorClasses.objects.filter(post_id=job_post).first()
        if post_exist:
            tutor_name = post_exist.tutor_id.tutorname
            raise serializers.ValidationError({"message": "This post has been appointed to another tutor", "tutor_name": tutor_name})
        
        data['tutor_id'] = tutor_profile
        data['post_id'] = job_post
        return data

    def create(self, validated_data):
        tutor_class = TutorClasses.objects.create(**validated_data)
        job_post = validated_data.get('post_id')
        job_post.status = Status.CLOSED
        return tutor_class
    
    def update(self, instance, validated_data):
        status = validated_data.get('finished', instance.finished)
        if status:
            instance.finished = True
        instance.save()
        return instance