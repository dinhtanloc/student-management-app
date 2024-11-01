from .models import User,Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate

from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import random



# serializers.py
from rest_framework import serializers
from firebase_admin import auth
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class FirebaseTokenSerializer(serializers.Serializer):
    id_token = serializers.CharField(write_only=True)

    def validate(self, data):
        id_token = data.get("id_token")
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email")

            # Kiểm tra người dùng trong Django
            user, created = User.objects.get_or_create(email=email, defaults={"username": uid})
            
            if created:
                Profile.objects.create(user=user)  # Tạo profile cho người dùng mới
            
            data["user"] = user
        except Exception as e:
            raise serializers.ValidationError("Token không hợp lệ hoặc đã hết hạn.")

        return data

class FirebaseRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=100)

    def create(self, validated_data):
        email = validated_data["email"]
        username = validated_data["username"]
        
        # Tạo người dùng trên Firebase Authentication
        try:
            firebase_user = auth.create_user(email=email, display_name=username)
            user, created = User.objects.get_or_create(email=email, defaults={"username": username})
            if created:
                Profile.objects.create(user=user)
            return user
        except Exception as e:
            raise serializers.ValidationError("Đăng ký thất bại.")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    # password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    # def validate(self, attrs):
    #     if attrs['password'] != attrs['password2']:
    #         raise serializers.ValidationError(
    #             {"password": "Password fields didn't match."})

    #     return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']

        )

        user.set_password(validated_data['password'])
        user.save()

        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    password = serializers.CharField(source='user.password', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    class Meta:
        model = Profile
        fields = ['user', 'full_name','phone','address','job','username','email','password', 'bio', 'image','date_joined',
        'verified']

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=False)
    confirm_password = serializers.CharField(required=False)

    def validate(self, data):
        if 'new_password' in data and 'confirm_password' in data:
            if data['new_password'] != data['confirm_password']:
                raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})

        user = authenticate(username=self.context['request'].user.username, password=data['current_password'])
        if not user:
            raise serializers.ValidationError({'current_password': 'Incorrect current password'})
        




class UserSerializer(serializers.ModelSerializer):
    is_teacher = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email','date_joined','is_teacher','is_superuser','profile')


