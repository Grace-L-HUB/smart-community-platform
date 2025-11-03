from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import (
    UserViewSet, UserRegisterView, UserLoginView, UserLogoutView,
    WeChatLoginView, CustomTokenObtainPairView
)

# 创建路由器
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # 根路径直接注册用户视图集


# 定义额外的路由
urlpatterns = [
    # 包含路由器路由
    path('', include(router.urls)),
    
    # 认证相关路由
    path('auth/register/', UserRegisterView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    
    # JWT相关路由
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # 微信登录路由
    path('auth/wechat/', WeChatLoginView.as_view(), name='wechat-login'),
]