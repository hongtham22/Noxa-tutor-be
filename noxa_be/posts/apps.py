# from django.apps import AppConfig


# class PostConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'posts'


# posts/apps.py
from django.apps import AppConfig

class PostsConfig(AppConfig):
    name = 'posts'

    def ready(self):
        import posts.signals