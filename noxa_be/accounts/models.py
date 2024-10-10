import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from .enums import *

# Create your models here.
class User (AbstractUser):
    # uuid user_id, username, password, email, created, last_updated
    user_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    role = models.CharField(choices=Role.choices, max_length=50)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
    )

    
    def __str__(self):
        return self.username

class TutorProfile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    tutorname = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    bio_link = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(choices=Gender.choices, max_length=50)
    educational_background = models.CharField(choices=EducationalBackground.choices, max_length=255, blank=True, null=True)

    @property
    def tutor_id(self):
        return self.user.user_id
    
    def __str__(self):
        return self.tutorname

 
class ParentProfile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    parentname = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(choices=Gender.choices, max_length=50)
    description = models.TextField(blank=True, null=True)

    @property
    def parent_id(self):
        return self.user_id
    
    def __str__(self):
        return self.parentname
    
class Certificates (models.Model):
    certificate_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tutor_id = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    evidence_link = models.URLField()

class JobPost (models.Model):
    post_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    parent_id = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(choices=Subject.choices, max_length=50)
    description = models.TextField(blank=True)
    status = models.CharField(choices=Status.choices, max_length=50, default=Status.PENDING_APPROVAL)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    grade = models.IntegerField()
    background_desired = models.CharField(choices=EducationalBackground.choices, max_length=255, blank=True)
    duration = models.FloatField(blank=True)
    session_per_week = models.IntegerField()
    wage_per_session = models.FloatField()
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
    subject = models.CharField(choices=Subject.choices, max_length=50)
    
    def __str__(self):
        return self.subject
    
class ClassTime (models.Model):
    post_id = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='class_times')
    class_id = models.ForeignKey(TutorClasses, on_delete=models.CASCADE, null=True)
    weekday = models.CharField(choices=Weekday.choices, max_length=50, null=True)
    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self):
        return self.post_id
    






