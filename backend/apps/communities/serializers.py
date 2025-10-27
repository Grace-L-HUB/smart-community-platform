from rest_framework import serializers
from .models import Community, Building, House, UserHouse


class CommunitySerializer(serializers.ModelSerializer):
    """小区序列化器"""
    class Meta:
        model = Community
        fields = ['id', 'name', 'address', 'property_company', 'contact_phone',
                  'total_buildings', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BuildingSerializer(serializers.ModelSerializer):
    """楼栋序列化器"""
    class Meta:
        model = Building
        fields = ['id', 'community', 'name', 'unit_count', 'floor_count',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HouseSerializer(serializers.ModelSerializer):
    """房屋序列化器"""
    class Meta:
        model = House
        fields = ['id', 'building', 'unit', 'floor', 'room_number', 'area',
                  'house_type', 'owner_name', 'owner_phone', 'status',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserHouseSerializer(serializers.ModelSerializer):
    """用户房产绑定序列化器"""
    class Meta:
        model = UserHouse
        fields = ['id', 'user', 'house', 'relation_type', 'start_date',
                  'end_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']