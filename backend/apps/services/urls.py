from django.urls import path, include, re_path
from django.views.generic import RedirectView

urlpatterns = [
    # 重定向到merchants应用的相应API，确保兼容性
    re_path(r'^services/(.*)$', RedirectView.as_view(url='/api/merchants/services/%(path)s', permanent=True)),
    re_path(r'^orders/(.*)$', RedirectView.as_view(url='/api/merchants/orders/%(path)s', permanent=True)),
    re_path(r'^reviews/(.*)$', RedirectView.as_view(url='/api/merchants/reviews/%(path)s', permanent=True)),
    # 或者使用简单路径重定向
    path('services/', RedirectView.as_view(url='/api/merchants/services/', permanent=True)),
    path('orders/', RedirectView.as_view(url='/api/merchants/orders/', permanent=True)),
    path('reviews/', RedirectView.as_view(url='/api/merchants/reviews/', permanent=True)),
]