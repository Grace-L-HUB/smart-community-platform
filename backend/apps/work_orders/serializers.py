from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import WorkOrder, WorkOrderComment, WorkOrderRating, Complaint


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


# ==================== 投诉建议序列化器 ====================

class ComplaintCreateSerializer(serializers.ModelSerializer):
    """居民端投诉建议创建序列化器"""

    class Meta:
        model = Complaint
        fields = ['house_id', 'type', 'title', 'content', 'image_urls']

    def validate_title(self, value):
        """验证标题长度"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(_("标题至少需要5个字符"))
        return value.strip()

    def validate_content(self, value):
        """验证内容长度"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(_("投诉内容至少需要10个字符"))
        return value.strip()

    def validate_image_urls(self, value):
        """验证图片URL数组"""
        if value and len(value) > 9:
            raise serializers.ValidationError(_("最多只能上传9张图片"))
        return value

    def create(self, validated_data):
        """创建投诉建议"""
        # 从request中获取用户ID
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user_id'] = request.user.id

        # 生成投诉ID
        import random
        while True:
            complaint_id = random.randint(1, 999999)
            if not Complaint.objects.filter(id=complaint_id).exists():
                validated_data['id'] = complaint_id
                break

        return super().create(validated_data)


class ComplaintListSerializer(serializers.ModelSerializer):
    """居民端投诉列表序列化器"""
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    can_reply = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'type', 'title', 'status', 'status_text',
                  'submitted_at', 'processed_at', 'can_reply']

    def get_can_reply(self, obj):
        """判断是否可以补充说明"""
        return obj.status in ['submitted', 'processing']


class ComplaintDetailSerializer(serializers.ModelSerializer):
    """居民端投诉详情序列化器"""
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    house_info = serializers.SerializerMethodField(read_only=True)
    can_reply = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'type', 'title', 'content', 'image_urls',
                  'status', 'status_text', 'house_info', 'submitted_at',
                  'processed_at', 'process_remark', 'can_reply']

    def get_house_info(self, obj):
        """获取房产信息"""
        try:
            from apps.communities.models import House
            house = House.objects.get(id=obj.house_id)
            return f"{house.community.name} - {house.building}栋{house.unit}单元{house.room}室"
        except:
            return "房产信息不完整"

    def get_can_reply(self, obj):
        """判断是否可以补充说明"""
        return obj.status in ['submitted', 'processing']


class ComplaintProcessSerializer(serializers.ModelSerializer):
    """物业端投诉处理序列化器"""

    class Meta:
        model = Complaint
        fields = ['status', 'process_remark']

    def validate_process_remark(self, value):
        """验证处理备注"""
        # 如果正在设置为已解决或已驳回状态，需要检查处理备注
        if self.initial_data.get('status') in ['resolved', 'rejected']:
            if not value or len(value.strip()) < 5:
                raise serializers.ValidationError(_("解决或驳回投诉时必须填写至少5个字符的处理备注"))
        return value.strip() if value else None

    def update(self, instance, validated_data):
        """更新投诉建议"""
        request = self.context.get('request')

        # 如果状态发生变化，设置处理时间和处理人员
        if 'status' in validated_data and validated_data['status'] != instance.status:
            if request and hasattr(request, 'user'):
                validated_data['processor_id'] = request.user.id
            validated_data['processed_at'] = timezone.now()

        return super().update(instance, validated_data)


class ComplaintManageListSerializer(serializers.ModelSerializer):
    """物业端投诉管理列表序列化器"""
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    user_info = serializers.SerializerMethodField(read_only=True)
    house_info = serializers.SerializerMethodField(read_only=True)
    pending_days = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'user_id', 'user_info', 'house_id', 'house_info',
                  'type', 'title', 'status', 'status_text', 'submitted_at',
                  'processed_at', 'pending_days']

    def get_user_info(self, obj):
        """获取用户信息"""
        try:
            user = obj.user if hasattr(obj, 'user') else None
            if user:
                return f"{user.username} ({user.phone})"
            return f"用户ID: {obj.user_id}"
        except:
            return f"用户ID: {obj.user_id}"

    def get_house_info(self, obj):
        """获取房产信息"""
        try:
            from apps.communities.models import House
            house = House.objects.get(id=obj.house_id)
            return f"{house.community.name} - {house.building}栋{house.unit}单元{house.room}室"
        except:
            return "房产信息不完整"

    def get_pending_days(self, obj):
        """计算待处理天数"""
        if obj.status == 'submitted':
            delta = timezone.now().date() - obj.submitted_at.date()
            return delta.days
        return 0


class ComplaintManageDetailSerializer(serializers.ModelSerializer):
    """物业端投诉管理详情序列化器"""
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    user_info = serializers.SerializerMethodField(read_only=True)
    house_info = serializers.SerializerMethodField(read_only=True)
    processor_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'user_id', 'user_info', 'house_id', 'house_info',
                  'type', 'title', 'content', 'image_urls', 'status',
                  'status_text', 'submitted_at', 'processed_at',
                  'processor_id', 'processor_info', 'process_remark']

    def get_user_info(self, obj):
        """获取用户信息"""
        try:
            user = obj.user if hasattr(obj, 'user') else None
            if user:
                return {"username": user.username, "phone": user.phone}
            return {"username": f"用户ID:{obj.user_id}", "phone": ""}
        except:
            return {"username": f"用户ID:{obj.user_id}", "phone": ""}

    def get_house_info(self, obj):
        """获取房产信息"""
        try:
            from apps.communities.models import House
            house = House.objects.get(id=obj.house_id)
            return {
                "community": house.community.name,
                "building": house.building,
                "unit": house.unit,
                "room": house.room
            }
        except:
            return {"community": "未知", "building": "", "unit": "", "room": ""}

    def get_processor_info(self, obj):
        """获取处理人员信息"""
        if obj.processor_id:
            try:
                processor = obj.processor if hasattr(obj, 'processor') else None
                if processor:
                    return processor.username
                return f"处理人员ID: {obj.processor_id}"
            except:
                return f"处理人员ID: {obj.processor_id}"
        return None