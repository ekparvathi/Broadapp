from rest_framework import serializers
from .models import Userinfo,Userpersonal_data

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=Userinfo
        fields='__all__'

    def validate_email(self, value):
        if Userinfo.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone_number(self, value):
        if Userinfo.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value



class LoginSerializer(serializers.Serializer):
    Email = serializers.EmailField()
    Password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('Email')
        password = data.get('Password')
        
        if not email or not password:
            raise serializers.ValidationError("Email and Password are required.")
        
        # Additional validation can be added here if needed
        return data
    


class ForgotpasswordphoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=Userinfo
        fields=('Phonenumber',)

class userdataSerializer(serializers.ModelSerializer):
    class Meta:
        model=Userpersonal_data
        fields='__all__'