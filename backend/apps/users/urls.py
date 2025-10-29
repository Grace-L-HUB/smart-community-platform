from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserRegisterView, UserLoginView, UserLogoutView
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
    

]