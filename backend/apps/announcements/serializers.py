from rest_framework import serializers
from .models import Announcement, AnnouncementRead


class AnnouncementSerializer(serializers.ModelSerializer):
    """公告序列化器"""
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'announcer', 'announcer_type',
                  'target_community', 'is_top', 'publish_status',
                  'publish_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'publish_time', 'created_at', 'updated_at']


class AnnouncementReadSerializer(serializers.ModelSerializer):
    """公告已读序列化器"""
    class Meta:
        model = AnnouncementRead
        fields = ['id', 'announcement', 'user', 'read_time']
        read_only_fields = ['id', 'read_time']