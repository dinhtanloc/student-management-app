from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from deepface import DeepFace
from face_verify.models import UserFace
import json

class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def profile(self):
        profile = Profile.objects.get(user=self)

    def __str__(self):
        return f"{self.username}: ({self.email})"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=1000)
    phone= models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    image = models.ImageField(upload_to="user_images", default="default.png")
    verified = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.full_name = instance.username 
        profile.save()


@receiver(post_save, sender=Profile)
def save_user_face_embedding(sender, instance, **kwargs):
    if instance.image:
        try:
            embedding = DeepFace.represent(img_path=instance.image.path, model_name="Facenet")[0]["embedding"]
            # Tạo hoặc cập nhật bản ghi UserFace
            UserFace.objects.update_or_create(
                user=instance.user,
                profile=instance,
                defaults={"embedding": json.dumps(embedding)},
            )
        except Exception as e:
            print(f"Lỗi khi trích xuất embedding: {e}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()