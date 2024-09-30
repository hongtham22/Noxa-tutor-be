from django.urls import path
from .views import get_users, get_user, create_tutor, create_parent

urlpatterns = [
    path('users/', get_users),
    path('users/<str:pk>/', get_user),
    path('tutor/', create_tutor),
    path('parent/', create_parent),
]