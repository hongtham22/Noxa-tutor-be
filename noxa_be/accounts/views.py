from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import User, TutorProfile, ParentProfile
from .account_serializer import UserSerializer, TutorProfileSerializer, ParentProfileSerializer



"""
APIView for object based on User mode
- model: model to be used [TutorProfile, ParentProfile]
- serializer: serializer to be used [TutorProfileSerializer, ParentProfileSerializer]

* method get: get all objects or get object by id[pk]
* method post: create new object: created by calling create method in serializer
* method put: update object by id[pk] : updated by calling update method in serializer
* method delete: delete object by id[pk] : delected User object by id[pk], then automatically deleted TutorProfile or ParentProfile object because of on_delete=models.CASCADE in User model
"""

class BaseView(APIView):
    model = None
    serializer = None

    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, user_id=pk)
            instance = get_object_or_404(self.model, user=user)
            serializer = self.serializer(instance)
        else:
            instances = self.model.objects.all()
            serializer = self.serializer(instances, many=True)
        
        return Response(serializer.data)
    
    def post(self, request):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        user = get_object_or_404(User, user_id=pk)
        instance = get_object_or_404(self.model, user=user)
        serializer = self.serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = get_object_or_404(User, user_id=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
       
class TutorView(BaseView):
    model = TutorProfile
    serializer = TutorProfileSerializer

class ParentView(BaseView):
    model = ParentProfile
    serializer = ParentProfileSerializer
    