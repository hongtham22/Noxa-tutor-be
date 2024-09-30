from inspect import isabstract
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

from noxa_be.accounts.enums import *

# Create your models here.
class User (AbstractUser):
    # uuid user_id, username, password, email, created, last_updated
    user_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    role = models.CharField(choices=Role.choices)
    
    def __str__(self):
        return self.username

class TutorProfile (User):
    tutorname = models.CharField(max_length=255)
    address = models.TextField()
    birthdate = models.DateField()
    bio_link = models.URLField()
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(choices=Gender.choices)
    educational_background = models.CharField(choices=EducationalBackground.choices)

    @property
    def tutor_id(self):
        return self.user_id

 
class ParentProfile (User):
    parentname = models.CharField(max_length=255)
    address = models.TextField()
    birthdate = models.DateField()
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(choices=Gender.choices)
    description = models.TextField()

    @property
    def parent_id(self):
        return self.user_id
    
class Certificates (models.Model):
    certificate_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tutor_id = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    evidence_link = models.URLField()

class JobPost (models.Model):
    post_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    parent_id = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    subject = models.CharField(choices=Subject.choices)
    description = models.TextField()
    status = models.CharField(choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    grade = models.IntegerField()
    background_desired = models.CharField(choices=EducationalBackground.choices)
    duration = models.FloatField()
    session_per_week = models.IntegerField()
    wage_per_hour = models.FloatField()
    student_number = models.IntegerField()
    address = models.TextField()

    def __str__(self):
        return self.post_id
    
class JobRegister (models.Model):
    post_id = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    tutor_id = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)

class TutorClasses (models.Model):
    class_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tutor_id = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    post_id = models.ForeignKey(JobPost, on_delete=models.CASCADE)  
    finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.class_id
    
class Feedback (models.Model):
    feedback_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    class_id = models.ForeignKey(TutorClasses, on_delete=models.CASCADE)
    parent_id = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    tutor_id = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    rating = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return self.feedback_id
    
class Notification (models.Model):
    notification_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.notification_id
    
class TutorSubject (models.Model):
    tutor_id = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    subject = models.CharField(choices=Subject.choices)
    
    def __str__(self):
        return self.subject
    
class ClassTime (models.Model):
    post_id = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    class_id = models.ForeignKey(TutorClasses, on_delete=models.CASCADE, null=True)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()

    def __str__(self):
        return self.post_id
    






