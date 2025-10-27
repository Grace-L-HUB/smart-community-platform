from rest_framework import serializers
from datetime import date

class StatisticBaseSerializer(serializers.Serializer):
    """统计基础序列化器"""
    start_date = serializers.DateField(default=date.today().replace(day=1), help_text="开始日期")
    end_date = serializers.DateField(default=date.today(), help_text="结束日期")
    community_id = serializers.IntegerField(required=False, help_text="小区ID")


class WorkOrderStatSerializer(serializers.Serializer):
    """工单统计序列化器"""
    total_count = serializers.IntegerField(help_text="总工单数量")
    pending_count = serializers.IntegerField(help_text="待处理工单数量")
    completed_count = serializers.IntegerField(help_text="已完成工单数量")
    processing_count = serializers.IntegerField(help_text="处理中工单数量")
    cancel_count = serializers.IntegerField(help_text="已取消工单数量")
    daily_trend = serializers.ListField(child=serializers.DictField(), help_text="每日趋势")


class UserStatSerializer(serializers.Serializer):
    """用户统计序列化器"""
    total_count = serializers.IntegerField(help_text="总用户数")
    active_count = serializers.IntegerField(help_text="活跃用户数")
    new_user_count = serializers.IntegerField(help_text="新增用户数")
    user_growth_trend = serializers.ListField(child=serializers.DictField(), help_text="用户增长趋势")


class MerchantStatSerializer(serializers.Serializer):
    """商户统计序列化器"""
    total_count = serializers.IntegerField(help_text="总商户数")
    active_count = serializers.IntegerField(help_text="活跃商户数")
    total_services = serializers.IntegerField(help_text="总服务数")
    total_orders = serializers.IntegerField(help_text="总订单数")
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="总销售额")