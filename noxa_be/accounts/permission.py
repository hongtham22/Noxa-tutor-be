from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class IsTutor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            user_role = get_role(request)
            if user_role == 'tutor':
                return True
            else:
                return False
        except AuthenticationFailed:
            return super().has_permission(request, view)
        
class IsParent(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
    
        try:
            role = get_role(request)
            if role == 'parent':
                return True
            else:
                return False
        except AuthenticationFailed:
            return super().has_permission(request, view)
        
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
    
        try:
            role = get_role(request)
            if role == 'admin':
                return True
            else:
                return False
        except AuthenticationFailed:
            return super().has_permission(request, view)
        
class IsAdminOrSpecificRole(BasePermission):
    """
    Cho phép truy cập nếu người dùng là admin hoặc có vai trò
    phù hợp với class hiện tại (tutor/parent).
    """
    def has_permission(self, request, view):
        # Nếu là admin, cho phép truy cập
        if request.user.role == 'admin':
            return True
        
        # Kiểm tra xem class hiện tại là TutorView hay ParentView
        if view.__class__.__name__ == 'TutorView' and request.user.role == 'tutor':
            return True
        elif view.__class__.__name__ == 'ParentView' and request.user.role == 'parent':
            return True

        # Nếu không thỏa mãn, từ chối quyền truy cập
        return False

def get_role(request):
    jwt_auth = JWTAuthentication()
    header = jwt_auth.get_header(request)
    raw_token = jwt_auth.get_raw_token(header)
    validated_token = jwt_auth.get_validated_token(raw_token)
    user_role = validated_token.get('role')
    return user_role