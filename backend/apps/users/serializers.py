from rest_framework import serializers
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'avatar_url', 'role_id',
            'is_active', 'is_staff', 'is_superuser', 'is_blacklisted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        # 更新用户基本信息
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'phone', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if not username and not phone:
            raise serializers.ValidationError('用户名或手机号必须提供一个')
        
        return attrs


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色序列化器"""
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'role_type', 'permissions', 'created_at']
        read_only_fields = ['id', 'created_at']