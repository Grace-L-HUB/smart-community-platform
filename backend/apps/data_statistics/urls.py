from django.urls import path
from .views import (
    WorkOrderStatisticsView,
    UserStatisticsView,
    MerchantStatisticsView,
    CommunityStatisticsView
)

urlpatterns = [
    path('work-orders/', WorkOrderStatisticsView.as_view(), name='work-order-statistics'),
    path('users/', UserStatisticsView.as_view(), name='user-statistics'),
    path('merchants/', MerchantStatisticsView.as_view(), name='merchant-statistics'),
    path('communities/<int:community_id>/', CommunityStatisticsView.as_view(), name='community-statistics'),
]