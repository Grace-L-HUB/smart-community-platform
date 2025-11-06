from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityViewSet, BuildingViewSet, HouseViewSet, UserHouseViewSet

router = DefaultRouter()
router.register('communities', CommunityViewSet)
router.register('buildings', BuildingViewSet)
router.register('houses', HouseViewSet)
router.register('user-houses', UserHouseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]