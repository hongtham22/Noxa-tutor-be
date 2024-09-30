from rest_framework import serializers
from .models import User, TutorProfile, ParentProfile


"""
Base serializer for User model, required when creating TutorProfile or ParentProfile
- fields: convert fields to JSON and vice versa,
  + read_only: fields that only can convert from model to JSON
  + write_only: fields that only can convert from JSON to model
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }


"""
User-based serializer
- user: UserSerializer, optional but required to create new record
- x_id: user_id from User model, read only (cuz TutorProfile doesn't have user_id field)
- fields: pnly required fields that need to be here in the first try to create, other fields can be added later

* method validate: check if user is provided when creating new record (user is required as json structure in request)
* method to_representation: convert None value to 'Not recorded' for better readability (before sending to client)
* method create: create new TutorProfile object by creating new User object first, then create TutorProfile object
* method update: update TutorProfile object by updating fields that provided in request (TutorProfile only)

"""
class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    tutor_id = serializers.UUIDField(source='user.user_id',read_only=True)

    class Meta:
        model = TutorProfile    
        fields = ['tutor_id', 'user', 'tutorname', 'address', 'birthdate', 'bio_link', 'phone_number', 'gender', 'educational_background']
        extra_kwargs = {
            'description': {'required': False},
            'birthdate': {'required': False},
            'bio_link': {'required': False},
            'educational_background': {'required': False},
            'tutor_id': {'read_only': True},
        }

    def validate(self, data):
        if not self.instance and 'user' not in data:
            raise serializers.ValidationError({"user": "This is required to create new record"})
        return data

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
    
    def update(self, instance, validated_data):
        instance.tutorname = validated_data.get('tutorname', instance.tutorname)
        instance.address = validated_data.get('address', instance.address)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.bio_link = validated_data.get('bio_link', instance.bio_link)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.educational_background = validated_data.get('educational_background', instance.educational_background)

        instance.save()
        return instance
    
class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    parent_id = serializers.UUIDField(source='user.user_id',read_only=True)

    class Meta:
        model = ParentProfile
        fields = ['parent_id', 'user', 'parentname', 'address', 'birthdate', 'phone_number', 'gender', 'description']
        extra_kwargs = {
            'description': {'required': False},
            'birthdate': {'required': False},
            'parent_id': {'read_only': True}
        }

    def validate(self, data):
        if not self.instance and 'user' not in data:
            raise serializers.ValidationError({"user": "This is required to create new record"})
        return data

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
    
    def update(self, instance, validated_data):
        instance.parentname = validated_data.get('parentname', instance.parentname)
        instance.address = validated_data.get('address', instance.address)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance
    