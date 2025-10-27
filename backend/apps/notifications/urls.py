from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mark-as-read/<int:pk>/', NotificationViewSet.as_view({'post': 'mark_as_read'}), name='mark-as-read'),
    path('mark-all-read/', NotificationViewSet.as_view({'post': 'mark_all_read'}), name='mark-all-read'),
]