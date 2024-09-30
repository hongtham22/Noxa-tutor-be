from django.urls import path
from .views import TutorView, ParentView

urlpatterns = [
    path('tutors/', TutorView.as_view()),
    path('tutors/<str:pk>/', TutorView.as_view()),
    path('parents/', ParentView.as_view()),
    path('parents/<str:pk>/', ParentView.as_view()),
]