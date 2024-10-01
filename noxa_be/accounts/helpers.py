from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role

    access_token = refresh.access_token
    access_token = refresh.access_token
    access_token['role'] = user.role
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def token_blacklisted(token):
    try:
        refresh_token = RefreshToken(token)
        refresh_token.blacklist()
        return True
    except Exception as e:
        return False