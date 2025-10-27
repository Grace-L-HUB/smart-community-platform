from rest_framework import serializers
# 注意：该应用的功能已整合到merchants应用中
# 这里保留基础结构以确保兼容性

# 如果需要，可以从merchants应用导入序列化器进行复用
from apps.merchants.serializers import (
    MerchantServiceSerializer,
    MerchantOrderSerializer,
    ServiceReviewSerializer
)