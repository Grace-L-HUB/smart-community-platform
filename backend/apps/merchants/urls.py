from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MerchantViewSet, MerchantServiceViewSet, MerchantOrderViewSet,
    ServiceReviewViewSet, CouponViewSet, MerchantPostViewSet,
    UserFavoriteViewSet, PostLikeViewSet, PostCommentViewSet
)

router = DefaultRouter()
router.register(r'merchants', MerchantViewSet)
router.register(r'services', MerchantServiceViewSet)
router.register(r'orders', MerchantOrderViewSet)
router.register(r'reviews', ServiceReviewViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'posts', MerchantPostViewSet)
router.register(r'favorites', UserFavoriteViewSet)
router.register(r'post-likes', PostLikeViewSet)
router.register(r'post-comments', PostCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]