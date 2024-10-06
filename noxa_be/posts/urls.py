from django.urls import path
from .views import PostView, PostSearchView

urlpatterns = [
    path('', PostView.as_view()),  
    path('<uuid:pk>/', PostView.as_view()),  
    path('search/', PostSearchView.as_view(),),  
]
