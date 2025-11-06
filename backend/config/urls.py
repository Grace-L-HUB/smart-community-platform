"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI 配置
schema_view = get_schema_view(
   openapi.Info(
      title="Smart Community Platform API",
      default_version='v1',
      description="智慧社区平台API文档",
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

from django.http import JsonResponse

def health_check(request):
    """健康检查端点"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Smart Community Platform API is running'
    })

urlpatterns = [
    path('admin/', admin.site.urls),

    # 健康检查
    path('health/', health_check, name='health-check'),

    # API文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API路由
    path('api/users/', include('apps.users.urls')),
    path('api/communities/', include('apps.communities.urls')),
    path('api/work-orders/', include('apps.work_orders.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/merchants/', include('apps.merchants.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/common/', include('apps.common.urls')),
    path('api/statistics/', include('apps.data_statistics.urls')),
    # 保留services的API路径以确保兼容性
    path('api/services/', include('apps.services.urls')),
]
