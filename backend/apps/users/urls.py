from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserRegisterView, UserLoginView, UserLogoutView,
    UserProfileView, AddressViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'addresses', AddressViewSet)

# 定义额外的路由
urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    
    # 认证相关路由
    path('api/auth/register/', UserRegisterView.as_view(), name='user-register'),
    path('api/auth/login/', UserLoginView.as_view(), name='user-login'),
    path('api/auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    
    # 用户资料路由
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
]