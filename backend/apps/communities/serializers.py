from rest_framework import serializers
from django.utils import timezone
from apps.users.models import User
from .models import Community, Building, House, UserHouse, PropertyFeeBill, VisitorPass


class CommunitySerializer(serializers.ModelSerializer):
    """小区序列化器"""
    buildings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = ['id', 'name', 'address', 'property_phone', 'fee_standard',
                  'buildings_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_buildings_count(self, obj):
        """获取楼栋数量"""
        return obj.buildings.count()


class BuildingDetailSerializer(serializers.ModelSerializer):
    """楼栋详情序列化器（包含小区信息）"""
    community_name = serializers.CharField(source='community.name', read_only=True)
    houses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Building
        fields = ['id', 'community', 'community_name', 'name', 'unit_count', 
                  'houses_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_houses_count(self, obj):
        """获取房屋数量"""
        return obj.houses.count()


class BuildingSerializer(serializers.ModelSerializer):
    """楼栋序列化器（简化版）"""
    community_name = serializers.CharField(source='community.name', read_only=True)
    
    class Meta:
        model = Building
        fields = ['id', 'community', 'community_name', 'name', 'unit_count']
        read_only_fields = ['id']


class HouseDetailSerializer(serializers.ModelSerializer):
    """房屋详情序列化器（包含楼栋和小区信息）"""
    building_name = serializers.CharField(source='building.name', read_only=True)
    community_name = serializers.CharField(source='building.community.name', read_only=True)
    community_id = serializers.IntegerField(source='building.community.id', read_only=True)
    
    class Meta:
        model = House
        fields = ['id', 'building', 'building_name', 'community_id', 'community_name',
                  'unit', 'number', 'area', 'owner_name']
        read_only_fields = ['id']


class HouseSerializer(serializers.ModelSerializer):
    """房屋序列化器（简化版）"""
    building_name = serializers.CharField(source='building.name', read_only=True)
    
    class Meta:
        model = House
        fields = ['id', 'building', 'building_name', 'unit', 'number', 'area', 'owner_name']
        read_only_fields = ['id']


class UserHouseSerializer(serializers.ModelSerializer):
    """用户房产绑定序列化器"""
    user_info = serializers.SerializerMethodField()
    house_info = serializers.SerializerMethodField()
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = UserHouse
        fields = ['id', 'user', 'house', 'user_info', 'house_info', 'relationship', 
                  'status', 'certificate_image', 'approved_by', 'approved_by_name', 
                  'approved_at']
        read_only_fields = ['id', 'approved_by', 'approved_at']
    
    def get_user_info(self, obj):
        """获取用户基本信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'phone': obj.user.phone
        }
    
    def get_house_info(self, obj):
        """获取房屋基本信息"""
        return {
            'id': obj.house.id,
            'address': str(obj.house),
            'area': float(obj.house.area),
            'unit': obj.house.unit,
            'number': obj.house.number
        }


class UserHouseApplicationSerializer(serializers.ModelSerializer):
    """用户房产绑定申请序列化器"""
    
    class Meta:
        model = UserHouse
        fields = ['house', 'relationship', 'certificate_image']
    
    def create(self, validated_data):
        """创建房产绑定申请"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def validate_house(self, value):
        """验证房屋是否已被当前用户绑定"""
        user = self.context['request'].user
        if UserHouse.objects.filter(user=user, house=value).exists():
            raise serializers.ValidationError("您已经绑定过该房屋")
        return value


class UserHouseApprovalSerializer(serializers.ModelSerializer):
    """用户房产绑定审批序列化器"""
    
    class Meta:
        model = UserHouse
        fields = ['status']
    
    def update(self, instance, validated_data):
        """更新审批状态"""
        if validated_data.get('status') in [UserHouse.StatusType.APPROVED, UserHouse.StatusType.REJECTED]:
            instance.approved_by = self.context['request'].user
            instance.approved_at = timezone.now()
        return super().update(instance, validated_data)


class PropertyFeeBillSerializer(serializers.ModelSerializer):
    """物业费账单序列化器"""
    house_info = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyFeeBill
        fields = ['id', 'house_id', 'house_info', 'billing_period', 'amount', 
                  'status', 'due_date', 'paid_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_house_info(self, obj):
        """获取房屋信息"""
        try:
            house = House.objects.get(id=obj.house_id)
            return str(house)
        except House.DoesNotExist:
            return f"房屋ID: {obj.house_id}"


class VisitorPassSerializer(serializers.ModelSerializer):
    """访客通行证序列化器"""
    house_info = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VisitorPass
        fields = ['id', 'user_id', 'house_id', 'user_info', 'house_info',
                  'visitor_name', 'visitor_phone', 'pass_code', 'valid_from', 
                  'valid_to', 'status', 'created_at']
        read_only_fields = ['id', 'user_id', 'pass_code', 'created_at']
    
    def get_house_info(self, obj):
        """获取房屋信息"""
        try:
            house = House.objects.get(id=obj.house_id)
            return str(house)
        except House.DoesNotExist:
            return f"房屋ID: {obj.house_id}"
    
    def get_user_info(self, obj):
        """获取用户信息"""
        try:
            user = User.objects.get(id=obj.user_id)
            return {
                'username': user.username,
                'phone': user.phone
            }
        except User.DoesNotExist:
            return f"用户ID: {obj.user_id}"