from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet, AnnouncementReadViewSet

router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet)
router.register(r'announcement-reads', AnnouncementReadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]