from django.urls import path
from .views import TutorView, ParentView, LoginView, RegisterView, LogoutView, foo_parent, foo_tutor
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('tutors/', TutorView.as_view()),
    path('tutors/<str:pk>/', TutorView.as_view()),
    path('parents/', ParentView.as_view()),
    path('parents/<str:pk>/', ParentView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('foo_parent/', foo_parent),
    path('foo_tutor/', foo_tutor),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]