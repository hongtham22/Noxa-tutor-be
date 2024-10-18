from django.urls import path

from application.views.post_view import AppointView, PostView, SearchView
from application.views.admin_post_view import AdminPostView
from application.views.tutor_post_view import TutorPostView
from application.views.enum_view import EnumView
from application.views.notification_view import sse_notification

urlpatterns = [
    path('posts/', PostView.as_view()),
    path('posts/<str:pk>/', PostView.as_view()),
    path('admin/posts/', AdminPostView.as_view()),
    path('admin/posts/<str:pk>/', AdminPostView.as_view()),
    path('enum/', EnumView.as_view()),
    path('tutor/posts/', TutorPostView.as_view()),
    path('tutor/posts/<str:pk>/', TutorPostView.as_view()),
    path('notifications/<str:parent_id>/', sse_notification),
    path('search/', SearchView.as_view()),
    path('appoint/', AppointView.as_view())
]
