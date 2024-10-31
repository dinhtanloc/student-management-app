from .models import UserFace
from accounts.models import User, Profile
# from .forms import UserFaceForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from django.conf import settings
from firebase_admin import auth
from deepface import DeepFace

@api_view(['POST'])
def upload_face(request):
    id_token = request.data.get('idToken')
    if not id_token:
        return Response({"error": "ID token not provided"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_info = auth.get_account_info(id_token)
        uid = user_info["users"][0]["localId"]
        django_user = User.objects.get(username=uid)  # Lấy User từ ID token

        # Tìm Profile tương ứng
        user_profile = django_user.profile

        # Tạo UserFace mới
        face_record = UserFace.objects.create(user=django_user, profile=user_profile)

        # Xử lý ảnh và tạo vector đặc trưng
        face_image_path = user_profile.image.path  # Lấy đường dẫn ảnh từ Profile
        face_embedding = DeepFace.represent(face_image_path, model_name='Facenet')[0]['embedding']
        face_record.embedding = json.dumps(face_embedding)
        face_record.save()

        return Response({"message": "Face uploaded successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)