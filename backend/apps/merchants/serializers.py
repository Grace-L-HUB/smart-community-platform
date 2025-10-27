from rest_framework import serializers
from .models import (
    Merchant, MerchantService, MerchantOrder, ServiceReview,
    Coupon, MerchantPost, UserFavorite, PostLike, PostComment, MerchantStat
)


class MerchantSerializer(serializers.ModelSerializer):
    """商户序列化器"""
    class Meta:
        model = Merchant
        fields = ['id', 'name', 'contact_person', 'contact_phone', 'email',
                  'business_license', 'logo', 'description', 'address',
                  'community', 'service_categories', 'business_hours', 'status',
                  'approved_by', 'approved_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'approved_by', 'approved_at', 'created_at', 'updated_at']


class MerchantServiceSerializer(serializers.ModelSerializer):
    """商户服务序列化器"""
    class Meta:
        model = MerchantService
        fields = ['id', 'merchant', 'name', 'description', 'price', 'unit',
                  'duration', 'images', 'cover_image', 'is_active', 'is_popular',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MerchantOrderSerializer(serializers.ModelSerializer):
    """商户订单序列化器"""
    class Meta:
        model = MerchantOrder
        fields = ['id', 'user', 'merchant_service', 'quantity', 'total_amount',
                  'status', 'scheduled_at', 'service_address', 'contact_name',
                  'contact_phone', 'payment_time', 'payment_method', 'payment_no',
                  'remarks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'payment_time', 'created_at', 'updated_at']


class ServiceReviewSerializer(serializers.ModelSerializer):
    """服务评价序列化器"""
    class Meta:
        model = ServiceReview
        fields = ['id', 'merchant_order', 'rating', 'content', 'images', 'created_at']
        read_only_fields = ['id', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    """优惠券序列化器"""
    class Meta:
        model = Coupon
        fields = ['id', 'merchant', 'title', 'description', 'image_url',
                  'start_date', 'end_date', 'view_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']


class MerchantPostSerializer(serializers.ModelSerializer):
    """商户动态序列化器"""
    class Meta:
        model = MerchantPost
        fields = ['id', 'merchant', 'title', 'content', 'images', 'like_count', 'created_at']
        read_only_fields = ['id', 'like_count', 'created_at']


class UserFavoriteSerializer(serializers.ModelSerializer):
    """用户收藏序列化器"""
    class Meta:
        model = UserFavorite
        fields = ['id', 'user', 'target_type', 'target_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PostLikeSerializer(serializers.ModelSerializer):
    """动态点赞序列化器"""
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class PostCommentSerializer(serializers.ModelSerializer):
    """动态评论序列化器"""
    class Meta:
        model = PostComment
        fields = ['id', 'user', 'post', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class MerchantStatSerializer(serializers.ModelSerializer):
    """商户统计序列化器"""
    class Meta:
        model = MerchantStat
        fields = ['id', 'merchant', 'date', 'page_views', 'favorite_count',
                  'coupon_views', 'created_at']
        read_only_fields = ['id', 'created_at']