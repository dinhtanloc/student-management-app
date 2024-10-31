from django.db import models
import json
from accounts.models import User, Profile

class UserFace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Khóa ngoại liên kết với User
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Khóa ngoại liên kết với Profile
    embedding = models.JSONField()  # Lưu trữ vector đặc trưng
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s face record"