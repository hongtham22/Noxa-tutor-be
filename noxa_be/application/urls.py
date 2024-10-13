from django.urls import path

from application.views.post_view import PostView, PostSearchView, PostSearch
from application.views.admin_post_view import AdminPostView
from application.views.enum_view import EnumView
from application.views.notification_view import sse_notification

urlpatterns = [
    path('posts/', PostView.as_view()),
    path('posts/<str:pk>/', PostView.as_view()),
    path('admin/posts/', AdminPostView.as_view()),
    path('admin/posts/<str:pk>', AdminPostView.as_view()),
    path('enum/', EnumView.as_view()),
    path('notifications/<str:parent_id>', sse_notification),

    path('posts/search', PostSearchView.as_view()),

    path('posts/test', PostSearch.as_view())
]
