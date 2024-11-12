from rest_framework import serializers
from accounts.models import *
from application.models import *

class ReactSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = JobPostReact
        fields = [
            'reaction_id',
            'post_id',
            'user_id',
            'reaction_type',
            'created_at',
        ]
    
    def create(self, validated_data):
        return super().create(validated_data)