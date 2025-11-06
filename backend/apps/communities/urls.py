from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunityViewSet, BuildingViewSet, HouseViewSet, 
    UserHouseViewSet, PropertyFeeBillViewSet, VisitorPassViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'communities', CommunityViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'houses', HouseViewSet)
router.register(r'user-houses', UserHouseViewSet)
router.register(r'property-bills', PropertyFeeBillViewSet)
router.register(r'visitor-passes', VisitorPassViewSet)

urlpatterns = [
    path('', include(router.urls)),
]