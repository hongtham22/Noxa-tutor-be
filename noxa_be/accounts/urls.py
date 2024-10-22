from django.urls import path
from .views import ActivateAccountView, AvatarView, ReverifyEmailView, TutorView, ParentView, LoginView, RegisterView, LogoutView, ChangePasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('tutors/', TutorView.as_view()),
    path('tutors/<str:pk>/', TutorView.as_view()),
    path('parents/', ParentView.as_view()),
    path('parents/<str:pk>/', ParentView.as_view()),
    path('profile/avatar/', AvatarView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', ActivateAccountView.as_view()),
    path('reverify-email/', ReverifyEmailView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
]