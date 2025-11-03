from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
import os
import requests
import uuid
from .models import User, UserRole
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    CustomTokenObtainPairSerializer, WeChatLoginSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义JWT令牌获取视图"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集，处理用户信息的增删改查"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """根据不同的操作设置不同的权限"""
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'], url_path='permissions')
    def get_user_permissions(self, request):
        """获取当前用户的权限信息"""
        user = request.user
        try:
            role = UserRole.objects.get(id=user.role_id)
            return Response({
                'role_id': user.role_id,
                'role_name': role.name,
                'role_type': role.role_type,
                'permissions': role.permissions
            })
        except UserRole.DoesNotExist:
            return Response({
                'role_id': None,
                'role_name': None,
                'role_type': None,
                'permissions': {}
            }, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, *args, **kwargs):
        """获取用户详情"""
        # 普通用户只能查看自己的信息，管理员可以查看所有用户信息
        instance = self.get_object()
        if request.user != instance and not request.user.is_superuser:
            return Response({'detail': '无权访问其他用户信息'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新用户信息"""
        # 普通用户只能更新自己的信息，管理员可以更新所有用户信息
        instance = self.get_object()
        if request.user != instance and not request.user.is_superuser:
            return Response({'detail': '无权修改其他用户信息'}, status=status.HTTP_403_FORBIDDEN)
        
        # 普通用户不能修改角色
        if not request.user.is_superuser:
            request.data.pop('role', None)
        
        return super().update(request, *args, **kwargs)


class UserRegisterView(APIView):
    """用户注册视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': '注册成功', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            phone = serializer.validated_data.get('phone')
            password = serializer.validated_data.get('password')
            
            # 尝试使用用户名或手机号登录
            user = None
            if username:
                user = authenticate(username=username, password=password)
            elif phone:
                try:
                    user_obj = User.objects.get(phone=phone)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None:
                login(request, user)
                return Response({
                    'message': '登录成功',
                    'user_id': user.id,
                    'username': user.username,
                    'role_id': user.role_id
                })
            return Response({'detail': '用户名/手机号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WeChatLoginView(APIView):
    """微信登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = WeChatLoginSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get('code')
            avatar_url = serializer.validated_data.get('avatar_url', '')
            nickname = serializer.validated_data.get('nickname', '')
            
            # 微信小程序AppID和AppSecret，实际应该从环境变量获取
            app_id = os.getenv('WECHAT_APPID', 'your_wechat_appid')
            app_secret = os.getenv('WECHAT_APPSECRET', 'your_wechat_appsecret')
            
            # 调用微信API获取openid和session_key
            url = f"https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={app_secret}&js_code={code}&grant_type=authorization_code"
            response = requests.get(url)
            result = response.json()
            
            # 检查是否获取成功
            if 'openid' not in result:
                return Response({
                    'detail': '微信登录失败',
                    'error': result.get('errmsg', '未知错误')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            openid = result.get('openid')
            
            # 查找是否已有该openid的用户
            try:
                user = User.objects.get(openid=openid)
            except User.DoesNotExist:
                # 创建新用户
                try:
                    # 生成唯一用户名
                    username = f"wx_{openid[:10]}_{str(uuid.uuid4())[:8]}"
                    user = User.objects.create_user(
                        username=username,
                        phone='',
                        password=None,  # 微信登录用户不需要密码
                        openid=openid,
                        avatar_url=avatar_url,
                        is_active=True
                    )
                    # 默认设置为居民角色（如果存在）
                    try:
                        resident_role = UserRole.objects.get(role_type='resident')
                        user.role_id = resident_role.id
                        user.save()
                    except UserRole.DoesNotExist:
                        pass
                except IntegrityError:
                    return Response({'detail': '创建用户失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 更新用户信息
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
                user.save()
            
            # 生成JWT令牌
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'role_id': user.role_id,
                'openid': user.openid
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """用户登出视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # JWT认证下的登出主要由前端处理，这里可以添加token到黑名单等逻辑
        # 清除session以支持旧的认证方式
        logout(request)
        return Response({'message': '登出成功'})
