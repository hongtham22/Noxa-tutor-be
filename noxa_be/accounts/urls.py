from django.urls import path
from .views import TutorView, ParentView, LoginView, RegisterView, foo
urlpatterns = [
    path('tutors/', TutorView.as_view()),
    path('tutors/<str:pk>/', TutorView.as_view()),
    path('parents/', ParentView.as_view()),
    path('parents/<str:pk>/', ParentView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('foo/', foo),
]