from datetime import timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
import os

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
    
def send_email_verification(user, request):
    token = RefreshToken.for_user(user)
    token = token.access_token
    token.set_exp(lifetime=timedelta(minutes=5))
    verify_url = f"{request.scheme}://{request.get_host()}/api/verify-email/?token={str(token)}"

    subject = 'Vui lòng xác thực email của bạn'
    
    # Rendering the HTML template with context
    html_message = render_to_string('email_verification.html', {
        'username': user.username,
        'verify_url': verify_url,
    })
    
    plain_message = strip_tags(html_message)

    # Create EmailMultiAlternatives object
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )

    # Attach HTML message
    email.attach_alternative(html_message, "text/html")
    
    # load 7 images in static/images folder to the mail
    static_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
    for i in range(1, 8):
        image_path = os.path.join(static_dir, f'image-{i}.png')
        with open(image_path, 'rb') as f:
            image = MIMEImage(f.read())
            image.add_header('Content-ID', f'<image{i}>')
            email.attach(image)

    email.send()

def decode_token(token):
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user_id = validated_token.get('user_id')
        return user_id
    except Exception as e:
        return None
    