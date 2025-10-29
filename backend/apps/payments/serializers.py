
from rest_framework import serializers
from .models import PaymentOrder


class PaymentOrderSerializer(serializers.ModelSerializer):
    """支付订单序列化器"""
    class Meta:
        model = PaymentOrder
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class PaymentOrderCreateSerializer(serializers.ModelSerializer):
    """创建支付订单序列化器"""
    class Meta:
        model = PaymentOrder
        fields = ('user_id', 'bill_id', 'amount')
        read_only_fields = ('id', 'order_number', 'status', 'payment_gateway', 'gateway_order_no', 'paid_at', 'created_at', 'updated_at')


class PaymentOrderPaySerializer(serializers.Serializer):
    """支付订单序列化器"""
    payment_gateway = serializers.ChoiceField(choices=PaymentOrder.GATEWAY_CHOICES, required=True)
    gateway_order_no = serializers.CharField(max_length=64, required=True)