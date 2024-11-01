from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from deepface import DeepFace
# from face_verify.models import UserFace
from django.contrib.postgres.fields import ArrayField

import firebase_admin
from firebase_admin import firestore 

import json
db = firestore.client()


class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def profile(self):
        profile = Profile.objects.get(user=self)

    def __str__(self):
        return f"{self.username}: ({self.email})"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.full_name = instance.username 
        profile.save()
        db.collection('users').document(str(instance.id)).set({
        "id": instance.id,
        "username": instance.username,
        "email": instance.email
    })

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=1000)
    phone= models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    image = models.ImageField(upload_to="user_images", default="default.png")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.id}-{self.full_name}"


class UserFace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    embedding = ArrayField(models.FloatField())  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s face record"
    
@receiver(post_save, sender=UserFace)
def sync_user_face_to_firestore(sender, instance, created, **kwargs):
    db.collection('user_faces').document(str(instance.id)).set({
        "user_id": instance.user.id,
        "embedding": instance.embedding,
        "created_at": instance.created_at.isoformat(), 
    })




@receiver(post_save, sender=Profile)
def save_user_face_embedding(sender, instance, **kwargs):
    if instance.image:
        db.collection('profiles').document(str(instance.id)).set({
                "id": instance.id,
                "user_id": instance.user.id,
                "full_name": instance.full_name,
                "phone": instance.phone,
                "address": instance.address,
                "image": str(instance.image),
                "verified": instance.verified
            })
        try:
            result = DeepFace.represent(img_path=instance.image.path, model_name="Facenet")
            embedding = result
            print(dict(enumerate(embedding)))  # In kết quả trả về để kiểm tra
            # Tạo hoặc cập nhật bản ghi UserFace
            UserFace.objects.update_or_create(
                user=instance.user,
                defaults={"embedding": list(embedding)},
            )
        except Exception as e:
            print(f"Lỗi khi trích xuất embedding: {e}")
    else:
        # Nếu không có ảnh, chỉ cập nhật các trường còn lại
        db.collection('profiles').document(str(instance.id)).update({
            "phone": instance.phone,
            "address": instance.address,
            "image": str(instance.image),
            "verified": instance.verified
        })

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()