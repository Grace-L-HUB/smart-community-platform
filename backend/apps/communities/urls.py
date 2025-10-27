from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityViewSet, BuildingViewSet, HouseViewSet, UserHouseViewSet

router = DefaultRouter()
router.register(r'communities', CommunityViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'houses', HouseViewSet)
router.register(r'user-houses', UserHouseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]