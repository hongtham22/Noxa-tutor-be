from django.urls import path

from application.views.post_view import PostView
from application.views.admin_post_view import AdminPostView

urlpatterns = [
    path('posts/', PostView.as_view()),
    path('posts/<str:pk>/', PostView.as_view()),
    path('admin/posts/', AdminPostView.as_view()),
]
