from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default='employee')
    class Meta:
        model = User
        fields = '__all__'