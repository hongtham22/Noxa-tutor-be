from django.urls import path

from application.views.post_view import PostView, SearchView
from application.views.admin_post_view import AdminPostView
from application.views.statistics_view import StatisticView
from application.views.tutor_post_view import TutorPostView
from application.views.enum_view import EnumView
from application.views.notification_view import sse_notification
from application.views.parent_class_view import AppointView, FeedbackView
from application.views.tutor_class_view import TutorClassView
from application.views.report_view import ReportView
from application.views.comment_view import JobPostCommentView
from application.views.react_view import JobPostReactView

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
    path('class/appoint/', AppointView.as_view()),
    path('class/feedback/', FeedbackView.as_view()),
    path('class/feedback/<str:id>/', FeedbackView.as_view()),
    path('tutor/class/', TutorClassView.as_view()),
    path('report/', ReportView.as_view()),
    path('report/<str:pk>/', ReportView.as_view()),
    path('statistics/', StatisticView.as_view()),
    path('postcomments/<str:pk>/', JobPostCommentView.as_view()),
    path('postcomments/', JobPostCommentView.as_view()),
    path('postlike/<str:pk>/', JobPostReactView.as_view()),
]
