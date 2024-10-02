from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user) -> Token:
        token = super().get_token(user)
        token['user_id'] = user.user_id
        token['role'] = user.role
        print('x')
        return token