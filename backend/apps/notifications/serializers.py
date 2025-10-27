from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    class Meta:
        model = Notification
        fields = ['id', 'type', 'receiver', 'sender', 'title', 'content',
                  'target_url', 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']