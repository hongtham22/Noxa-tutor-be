from rest_framework import serializers
from accounts.models import *

class JobPostSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = JobPost
        fields = '__all__'

    def get_parent_name(self, obj):
        return obj.parent_id.parentname

