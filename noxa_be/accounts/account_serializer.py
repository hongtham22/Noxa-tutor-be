from rest_framework import serializers
from .models import User, TutorProfile, ParentProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    tutor_id = serializers.UUIDField(source='user.user_id',read_only=True)

    class Meta:
        model = TutorProfile    
        fields = ['tutor_id', 'user', 'tutorname', 'address', 'birthdate', 'bio_link', 'phone_number', 'gender', 'educational_background']
        extra_kwargs = {
            'description': {'required': False},
            'birthdate': {'required': False},
            'bio_link': {'required': False},
            'educational_background': {'required': False},
            'tutor_id': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        for field in representation:
            if representation[field] is None:
                representation[field] = 'Not recorded'
        
        return representation
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        tutor_profile = TutorProfile.objects.create(user=user, **validated_data)
        return tutor_profile
    
class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    parent_id = serializers.UUIDField(source='user.user_id',read_only=True)

    class Meta:
        model = ParentProfile
        fields = ['parent_id', 'user', 'parentname', 'address', 'birthdate', 'phone_number', 'gender', 'description']
        extra_kwargs = {
            'description': {'required': False},
            'birthdate': {'required': False},
            'parent_id': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        for field in representation:
            if representation[field] is None:
                representation[field] = 'Not recorded'
        
        return representation


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        parent_profile = ParentProfile.objects.create(user=user, **validated_data)
        return parent_profile
    