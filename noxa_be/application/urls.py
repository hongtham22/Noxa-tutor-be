from django.urls import path

from application.views.post_view import PostView

urlpatterns = [
    path('posts/', PostView.as_view()),
    path('posts/<str:pk>/', PostView.as_view()),
]
