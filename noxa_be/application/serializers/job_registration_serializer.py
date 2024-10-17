from rest_framework import serializers

from accounts.models import JobPost, JobRegister, TutorProfile, User
from accounts.enums import Status

class JobRegistrationSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    class Meta:
        model = JobRegister
        fields = '__all__'
        extra_kwargs = {
            'registration_id': {'read_only': True},
            'tutor_name': {'read_only': True},
            'post_id': {'write_only': True},
            'tutor_id': {'required': True},
        }

    def to_internal_value(self, data):
        data = data.copy()

        post_id = data.get('post_id')
        tutor_id = data.get('tutor_id')

        if post_id:
            post = JobPost.objects.get(post_id=post_id)
            if not post:
                raise serializers.ValidationError({"post_id": "Post not found"})
        if tutor_id:
            tutor = User.objects.get(user_id=tutor_id)
            tutor_profile = TutorProfile.objects.filter(user=tutor).exists()
            if not tutor_profile:
                raise serializers.ValidationError({"tutor_id": "Tutor not found"})
            
        # check if post hasn't been approved
        if post.status != Status.APPROVED:
            raise serializers.ValidationError({"post_id": "This post is not approved by admin"})
            
        if JobRegister.objects.filter(post_id=post_id, tutor_id=tutor_id).exists():
            raise serializers.ValidationError({"tutor_id": "Tutor had registered this class"})

        data['post_id'] = post
        data['tutor_id'] = tutor
        return data
        
    def get_tutor_name(self, obj):
        tutor = TutorProfile.objects.get(user=obj.tutor_id)
        return tutor.tutorname
