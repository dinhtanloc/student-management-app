from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import json
from scipy.spatial.distance import cosine
from deepface import DeepFace
from .models import UserFace

class FaceLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        image_path = request.data.get('image_path')  # Nhận đường dẫn ảnh từ yêu cầu
        user_id = request.data.get('user_id')  # Nhận ID người dùng từ yêu cầu

        try:
            user_embedding = DeepFace.represent(img_path=image_path, model_name="Facenet")[0]["embedding"]

            user_faces = UserFace.objects.all()
            min_distance = float('inf')
            matched_user = None

            for face in user_faces:
                stored_embedding = json.loads(face.embedding)
                distance = cosine(user_embedding, stored_embedding)

                if distance < min_distance:
                    min_distance = distance
                    matched_user = face.user

            THRESHOLD = 0.5  
            if min_distance < THRESHOLD and matched_user and matched_user.id == user_id:
                refresh = RefreshToken.for_user(matched_user)  # Tạo JWT cho người dùng
                return Response({
                    "status": "success",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
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
