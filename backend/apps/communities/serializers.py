from rest_framework import serializers
from .models import Community, Building, House, UserHouse


class CommunitySerializer(serializers.ModelSerializer):
    """小区序列化器"""
    buildings_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Community
        fields = [
            'id', 'name', 'address', 'property_phone', 'fee_standard',
            'buildings_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_buildings_count(self, obj):
        """获取楼栋数量"""
        return obj.buildings.count()

    def validate_fee_standard(self, value):
        """验证物业费标准"""
        if value <= 0:
            raise serializers.ValidationError("物业费标准必须大于0")
        return value

    def validate_name(self, value):
        """验证小区名称"""
        if not value.strip():
            raise serializers.ValidationError("小区名称不能为空")
        return value.strip()


class CommunityDetailSerializer(CommunitySerializer):
    """小区详情序列化器（包含楼栋信息）"""
    buildings = serializers.SerializerMethodField(read_only=True)

    class Meta(CommunitySerializer.Meta):
        fields = CommunitySerializer.Meta.fields + ['buildings']

    def get_buildings(self, obj):
        """获取楼栋列表"""
        buildings = obj.buildings.all()
        return BuildingListSerializer(buildings, many=True).data


class BuildingSerializer(serializers.ModelSerializer):
    """楼栋序列化器"""
    community_name = serializers.CharField(source='community.name', read_only=True)
    houses_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Building
        fields = [
            'id', 'community', 'community_name', 'name', 'unit_count',
            'houses_count'
        ]
        read_only_fields = ['id']

    def get_houses_count(self, obj):
        """获取房屋数量"""
        return obj.houses.count()

    def validate_name(self, value):
        """验证楼栋名称"""
        if not value.strip():
            raise serializers.ValidationError("楼栋名称不能为空")
        return value.strip()

    def validate_unit_count(self, value):
        """验证单元数"""
        if value <= 0:
            raise serializers.ValidationError("单元数必须大于0")
        return value


class BuildingListSerializer(serializers.ModelSerializer):
    """楼栋列表序列化器（简化版）"""
    class Meta:
        model = Building
        fields = ['id', 'name', 'unit_count']


class HouseSerializer(serializers.ModelSerializer):
    """房屋序列化器"""
    building_info = serializers.SerializerMethodField(read_only=True)
    full_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = House
        fields = [
            'id', 'building', 'building_info', 'unit', 'number', 'area',
            'owner_name', 'full_address'
        ]
        read_only_fields = ['id']

    def get_building_info(self, obj):
        """获取楼栋基本信息"""
        return {
            'id': obj.building.id,
            'name': obj.building.name,
            'community_name': obj.building.community.name
        }

    def get_full_address(self, obj):
        """获取完整地址"""
        return f"{obj.building.community.name}-{obj.building.name}-{obj.unit}栋-{obj.number}室"

    def validate_area(self, value):
        """验证建筑面积"""
        if value <= 0:
            raise serializers.ValidationError("建筑面积必须大于0")
        return value

    def validate_number(self, value):
        """验证房号"""
        if not value.strip():
            raise serializers.ValidationError("房号不能为空")
        return value.strip()


class HouseListSerializer(serializers.ModelSerializer):
    """房屋列表序列化器（简化版）"""
    full_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = House
        fields = ['id', 'unit', 'number', 'area', 'full_address']

    def get_full_address(self, obj):
        """获取完整地址"""
        return f"{obj.building.community.name}-{obj.building.name}-{obj.unit}栋-{obj.number}室"


class UserHouseSerializer(serializers.ModelSerializer):
    """用户房产绑定序列化器"""
    user_info = serializers.SerializerMethodField(read_only=True)
    house_info = serializers.SerializerMethodField(read_only=True)
    full_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserHouse
        fields = [
            'id', 'user', 'user_info', 'house', 'house_info', 'full_address',
            'relationship', 'status', 'certificate_image',
            'approved_by', 'approved_at'
        ]
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
            'unit': obj.house.unit,
            'number': obj.house.number,
            'area': obj.house.area
        }

    def get_full_address(self, obj):
        """获取完整地址"""
        return f"{obj.house.building.community.name}-{obj.house.building.name}-{obj.house.unit}栋-{obj.house.number}室"

    def validate(self, attrs):
        """验证用户房产绑定"""
        user = attrs.get('user')
        house = attrs.get('house')

        # 检查是否已经绑定过
        if UserHouse.objects.filter(user=user, house=house).exists():
            raise serializers.ValidationError("该用户已经绑定了此房产")

        return attrs


class UserHouseCreateSerializer(serializers.ModelSerializer):
    """用户房产绑定创建序列化器（简化版）"""
    class Meta:
        model = UserHouse
        fields = ['house', 'relationship', 'certificate_image']

    def validate(self, attrs):
        """验证绑定申请"""
        house = attrs.get('house')
        certificate_image = attrs.get('certificate_image')

        # 如果是业主，必须有房产证照片
        if attrs.get('relationship') == 'owner' and not certificate_image:
            raise serializers.ValidationError("业主绑定必须上传房产证照片")

        return attrs


class UserHouseApprovalSerializer(serializers.ModelSerializer):
    """用户房产绑定审核序列化器"""
    class Meta:
        model = UserHouse
        fields = ['status', 'approved_by']
        read_only_fields = ['approved_by']

    def validate_status(self, value):
        """验证审核状态"""
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("审核状态只能是 'approved' 或 'rejected'")
        return value