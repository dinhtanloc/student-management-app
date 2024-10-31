from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)  # Tạo JWT cho người dùng
            return Response({
                "status": "success",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.profile.full_name,
                    "bio": user.profile.bio,
                    "phone": user.profile.phone,
                    "address": user.profile.address,
                    "job": user.profile.job,
                    "image": str(user.profile.image),
                    "verified": user.profile.verified,
                }
            })
        else:
            return Response({"status": "failed", "message": "Invalid email or password"}, status=401)
