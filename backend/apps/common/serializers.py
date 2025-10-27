from rest_framework import serializers
# common应用通常包含共享模型或实用功能
# 如果有共享模型，可以在这里定义相应的序列化器

class ResponseSerializer(serializers.Serializer):
    """通用响应序列化器"""
    code = serializers.IntegerField(default=200, help_text="状态码")
    message = serializers.CharField(default="success", help_text="响应消息")
    data = serializers.JSONField(help_text="响应数据")