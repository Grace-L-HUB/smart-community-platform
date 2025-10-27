from rest_framework import serializers
from .models import WorkOrder, WorkOrderComment, WorkOrderRating


class WorkOrderSerializer(serializers.ModelSerializer):
    """工单序列化器"""
    class Meta:
        model = WorkOrder
        fields = ['id', 'user', 'community', 'house', 'type', 'title',
                  'description', 'images', 'status', 'assigned_to',
                  'completion_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'completion_time', 'created_at', 'updated_at']


class WorkOrderCommentSerializer(serializers.ModelSerializer):
    """工单留言序列化器"""
    class Meta:
        model = WorkOrderComment
        fields = ['id', 'work_order', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class WorkOrderRatingSerializer(serializers.ModelSerializer):
    """工单评价序列化器"""
    class Meta:
        model = WorkOrderRating
        fields = ['id', 'work_order', 'user', 'rating', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']