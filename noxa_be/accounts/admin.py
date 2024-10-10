from django.contrib import admin
from django.apps import apps

# Lấy tất cả các model trong ứng dụng hiện tại
models = apps.get_models()

# Đăng ký tất cả các model với admin site
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass  # Bỏ qua nếu model đã được đăng ký