from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet, WorkOrderCommentViewSet, WorkOrderRatingViewSet

router = DefaultRouter()
router.register(r'work-orders', WorkOrderViewSet)
router.register(r'comments', WorkOrderCommentViewSet)
router.register(r'ratings', WorkOrderRatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]