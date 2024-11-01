# middleware.py
from firebase_admin import auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User
class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        id_token = request.headers.get("Authorization")
        
        if not id_token:
            return None

        try:
            decoded_token = auth.verify_id_token(id_token)
            email = decoded_token.get("email")
            user, created = User.objects.get_or_create(email=email)
            return (user, None)
        except Exception:
            raise AuthenticationFailed("Lỗi xác thực Firebase")
