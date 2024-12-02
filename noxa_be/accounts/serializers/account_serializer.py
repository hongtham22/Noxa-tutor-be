from rest_framework import serializers
from accounts.enums import EducationalBackground, Gender
from ..models import User, TutorProfile, ParentProfile

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        try:
            email = validated_data.get('email')
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({"email": "This email is already taken."})
            
            username = validated_data.get('username')
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})

            user = User.objects.create_user(**validated_data)
            user.is_active = False
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Error in UserSerializer create: {str(e)}")
    
    def change_password(self, instance, validated_data):
        try:
            old_password = validated_data.get('old_password')
            new_password = validated_data.get('new_password')

            if not instance.check_password(old_password):
                raise serializers.ValidationError({"old_password": "Wrong password."})

            instance.set_password(new_password)
            instance.save()
            return instance
        except Exception as e:
            raise serializers.ValidationError(f"Error in UserSerializer change_password: {str(e)}")

class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    tutor_id = serializers.UUIDField(source='user.user_id', read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_feedback = serializers.SerializerMethodField()

    class Meta:
        model = TutorProfile    
        fields = ['tutor_id', 'user', 'tutorname', 'address', 'birthdate', 'bio_link', 'phone_number', 'gender', 'educational_background', 'avatar',  'average_rating', 'total_feedback']
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
            'average_rating': {'read_only': True},
            'total_feedback': {'read_only': True}
        }

    def validate(self, data):
        try:
            if not self.instance and 'user' not in data:
                raise serializers.ValidationError({"user": "This is required to create new record"})
            return data
        except Exception as e:
            raise serializers.ValidationError(f"Error in TutorProfileSerializer validate: {str(e)}")

    def to_representation(self, instance):
        try:
            representation = super().to_representation(instance)
            
            for field in representation:
                if representation[field] is None:
                    representation[field] = 'Not recorded'

                elif field == 'gender':
                    representation[field] = Gender.map_value_to_display(representation[field])
                
                elif field == 'educational_background':
                    representation[field] = EducationalBackground.map_value_to_display(representation[field])
            
            return representation
        except Exception as e:
            raise serializers.ValidationError(f"Error in TutorProfileSerializer to_representation: {str(e)}")
    
    def to_internal_value(self, data):
        try:
            data = data.copy()

            gender = data.get('gender', None)
            if gender:
                data['gender'] = Gender.map_display_to_value(str(gender))

            educational_background = data.get('educational_background', None)
            if educational_background:
                data['educational_background'] = EducationalBackground.map_display_to_value(educational_background)

            return data
        except Exception as e:
            raise serializers.ValidationError(f"Error in TutorProfileSerializer to_internal_value: {str(e)}")
        
    def create(self, validated_data):
        try:
            user_data = validated_data.pop('user')
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            user.is_active = False
            user.save()
            tutor_profile = TutorProfile.objects.create(user=user, **validated_data)
            return tutor_profile
        except Exception as e:
            raise serializers.ValidationError(f"Error in TutorProfileSerializer create: {str(e)}")
    
    def update(self, instance, validated_data):
        try:
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
        except Exception as e:
            raise serializers.ValidationError(f"Error in TutorProfileSerializer update: {str(e)}")
    
    def get_average_rating(self, obj):
        try:
            tutor_feedbacks = obj.feedback_set.all()
            total = 0
            for feedback in tutor_feedbacks:
                total += feedback.rating
            if len(tutor_feedbacks) == 0:
                return 0
            return total / len(tutor_feedbacks)
        except Exception as e:
            raise serializers.ValidationError(f"Error in TutorProfileSerializer get_average_rating: {str(e)}")
    
    def get_total_feedback(self, obj):
        try:
            return obj.feedback_set.count()
        except Exception as e:
            raise serializers.ValidationError(f"Error in TutorProfileSerializer get_total_feedback: {str(e)}")

class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    parent_id = serializers.UUIDField(source='user.user_id', read_only=True)

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
        try:
            if not self.instance and 'user' not in data:
                raise serializers.ValidationError({"user": "This is required to create new record"})
            return data
        except Exception as e:
            raise serializers.ValidationError(f"Error in ParentProfileSerializer validate: {str(e)}")
    
    def to_internal_value(self, data):
        try:
            data = data.copy()

            gender = data.get('gender', None)
            if gender:
                data['gender'] = Gender.map_display_to_value(str(gender))

            return data
        except Exception as e:
            raise serializers.ValidationError(f"Error in ParentProfileSerializer to_internal_value: {str(e)}")

    def to_representation(self, instance):
        try:
            representation = super().to_representation(instance)
            
            for field in representation:
                if representation[field] is None:
                    representation[field] = 'Not recorded'

                elif field == 'gender':
                    representation[field] = Gender.map_value_to_display(representation[field])
            
            return representation
        except Exception as e:
            raise serializers.ValidationError(f"Error in ParentProfileSerializer to_representation: {str(e)}")

    def create(self, validated_data):
        try:
            user_data = validated_data.pop('user')
            user = User.objects.create_user(**user_data)
            user.is_active = False
            user.save()
            parent_profile = ParentProfile.objects.create(user=user, **validated_data)
            return parent_profile
        except Exception as e:
            raise serializers.ValidationError(f"Error in ParentProfileSerializer create: {str(e)}")
    
    def update(self, instance, validated_data):
        try:
            instance.parentname = validated_data.get('parentname', instance.parentname)
            instance.address = validated_data.get('address', instance.address)
            instance.birthdate = validated_data.get('birthdate', instance.birthdate)
            instance.phone_number = validated_data.get('phone_number', instance.phone_number)
            instance.description = validated_data.get('description', instance.description)
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
        except Exception as e:
            raise serializers.ValidationError(f"Error in ParentProfileSerializer update: {str(e)}") 