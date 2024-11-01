from firebase_admin import auth  # Thêm Firebase Admin SDK
from django.contrib.auth import authenticate 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import FirebaseTokenSerializer, FirebaseRegisterSerializer
from rest_framework.response import Response

class FirebaseLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FirebaseTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response({"username": user.username, "email": user.email})

class FirebaseRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FirebaseRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"username": user.username, "email": user.email})



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print('email',email, "password", password)

        user = authenticate(email=email, password=password)
        if user:
            firebase_token = auth.create_custom_token(str(user.id))
            return Response({
                "status": "success",
                "firebase_token": firebase_token.decode(),  # Chuyển đổi nếu cần
                "user": {
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.profile.full_name,
                    "phone": user.profile.phone,
                    "address": user.profile.address,
                    "image": str(user.profile.image),
                    "verified": user.profile.verified,
                }
            })
        return Response({"status": "failed", "message": "Invalid email or password"}, status=401)
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Lấy thông tin người dùng đã đăng nhập
        user = request.user
        user_data = {
            "username": user.username,
            "email": user.email,
            "full_name": user.profile.full_name,
            "bio": user.profile.bio,
            "phone": user.profile.phone,
            "address": user.profile.address,
            "job": user.profile.job,
            "image": str(user.profile.image),
            "verified": user.profile.verified,
        }
        return Response({"status": "success", "user": user_data})
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
import json
from scipy.spatial.distance import cosine
from deepface import DeepFace
from firebase_admin import auth  # Thêm Firebase Admin SDK
from .models import UserFace

class FaceLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        image_path = request.data.get('image_path')  # Nhận đường dẫn ảnh từ yêu cầu
        user_id = request.data.get('user_id')  # Nhận ID người dùng từ yêu cầu

        try:
            # Trích xuất embedding của khuôn mặt từ ảnh đã cung cấp
            user_embedding = DeepFace.represent(img_path=image_path, model_name="Facenet")[0]["embedding"]

            # Tìm kiếm khuôn mặt người dùng trong cơ sở dữ liệu
            user_faces = UserFace.objects.all()
            min_distance = float('inf')
            matched_user = None

            for face in user_faces:
                stored_embedding = json.loads(face.embedding)
                distance = cosine(user_embedding, stored_embedding)

                if distance < min_distance:
                    min_distance = distance
                    matched_user = face.user

            THRESHOLD = 0.5  # Ngưỡng nhận diện khuôn mặt
            if min_distance < THRESHOLD and matched_user and matched_user.id == user_id:
                # Tạo token Firebase cho người dùng được nhận diện
                firebase_token = auth.create_custom_token(str(matched_user.id))  # Tạo token Firebase từ user ID
                return Response({
                    "status": "success",
                    "firebase_token": firebase_token.decode("utf-8"),  # Token được trả về dưới dạng chuỗi
                    "user": {
                        "email": matched_user.email,
                        "username": matched_user.username,
                        "full_name": matched_user.profile.full_name,
                        "bio": matched_user.profile.bio,
                        "phone": matched_user.profile.phone,
                        "address": matched_user.profile.address,
                        "job": matched_user.profile.job,
                        "image": str(matched_user.profile.image),
                        "verified": matched_user.profile.verified,
                    }
                })
            else:
                return Response({"status": "failed", "message": "Face not recognized"}, status=401)
        except Exception as e:
            return Response({"status": "failed", "message": f"Error during face recognition: {e}"}, status=500)
