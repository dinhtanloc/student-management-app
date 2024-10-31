import json
from django.contrib.auth import authenticate
from firebase_admin import auth as firebase_auth
from deepface import DeepFace
from scipy.spatial.distance import cosine
from .models import UserFace, User

from rest_framework_simplejwt.tokens import RefreshToken



def login_with_password(email, password):
    user = authenticate(email=email, password=password)
    if user:
        refresh = RefreshToken.for_user(user)  # Tạo JWT cho người dùng
        return {
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
        }
    else:
        return {"status": "failed", "message": "Invalid email or password"}



def login_with_face(image_path, user_id):
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
            return {
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
            }
        else:
            return {"status": "failed", "message": "Face not recognized"}
    except Exception as e:
        return {"status": "failed", "message": f"Error during face recognition: {e}"}
