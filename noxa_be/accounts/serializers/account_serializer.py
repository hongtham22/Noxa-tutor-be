from rest_framework import serializers

from accounts.enums import EducationalBackground, Gender
from ..models import User, TutorProfile, ParentProfile


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

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        print (user)
        return user


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
        fields = ['tutor_id', 'user', 'tutorname', 'address', 'birthdate', 'bio_link', 'phone_number', 'gender', 'educational_background', 'avatar']
        extra_kwargs = {
            'description': {'required': False},
            'phone_number': {'required': False},
            'gender': {'required': False},
            'avatar': {'required': False},
            'tutorname': {'required': False},
            'address': {'required': False},
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

            elif field == 'gender':
                representation[field] = Gender.map_value_to_display(representation[field])
            
            elif field == 'educational_background':
                representation[field] = EducationalBackground.map_value_to_display(representation[field])
                                                                                   
        
        return representation
    
    def to_internal_value(self, data):
        data = data.copy()

        gender = data.get('gender', None)
        if gender:
            data['gender'] = Gender.map_display_to_value(str(gender))

        educational_background = data.get('educational_background', None)
        if educational_background:
            data['educational_background'] = EducationalBackground.map_display_to_value(educational_background)

        return data
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        user.is_active = False
        user.save()
        tutor_profile = TutorProfile.objects.create(user=user, **validated_data)
        print (tutor_profile)
        return tutor_profile
    
    def update(self, instance, validated_data):
        instance.tutorname = validated_data.get('tutorname', instance.tutorname)
        instance.address = validated_data.get('address', instance.address)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.bio_link = validated_data.get('bio_link', instance.bio_link)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.educational_background = validated_data.get('educational_background', instance.educational_background)
        instance.gender = validated_data.get('gender', instance.gender)
        
        avatar = validated_data.get('avatar', None)
        if avatar:
            if isinstance(avatar, list):  
                avatar = avatar[0] 
            instance.avatar = avatar

        if instance.avatar is None:
            if instance.gender == Gender.MALE:
                instance.avatar = 'avatars/common_male.png'
            elif instance.gender == Gender.FEMALE:
                instance.avatar = 'avatars/common_female.png'
        instance.save()

        return instance
    
class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    parent_id = serializers.UUIDField(source='user.user_id',read_only=True)

    class Meta:
        model = ParentProfile
        fields = ['parent_id', 'user', 'parentname', 'address', 'birthdate', 'phone_number', 'gender', 'description', 'avatar']
        extra_kwargs = {
            'description': {'required': False},
            'birthdate': {'required': False},
            'phone_number': {'required': False},
            'parentname': {'required': False},
            'address': {'required': False},
            'gender': {'required': False},
            'avatar': {'required': False},
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
        user.is_active = False
        user.save()
        parent_profile = ParentProfile.objects.create(user=user, **validated_data)
        return parent_profile
    
    def update(self, instance, validated_data):
        instance.parentname = validated_data.get('parentname', instance.parentname)
        instance.address = validated_data.get('address', instance.address)
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.description = validated_data.get('description', instance.description)
        instance.gender = validated_data.get('gender', instance.gender)

        if instance.gender == Gender.MALE:
            instance.avatar = 'avatars/common_male.png'
        elif instance.gender == Gender.FEMALE:
            instance.avatar = 'avatars/common_female.png'

        instance.save()
        return instance
    