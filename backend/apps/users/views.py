from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer
)


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


class UserLogoutView(APIView):
    """用户登出视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': '登出成功'})
