from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserRegisterView, UserLoginView, UserLogoutView,
    UserProfileView, AddressViewSet, UserRoleViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # 根路径直接注册用户视图集
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'roles', UserRoleViewSet, basename='user-role')

# 定义额外的路由
urlpatterns = [
    # 包含路由器路由
    path('', include(router.urls)),
    
    # 认证相关路由
    path('auth/register/', UserRegisterView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    
    # 用户资料路由
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]