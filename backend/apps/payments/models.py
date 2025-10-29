from django.db import models
import uuid
import datetime


class PaymentOrder(models.Model):
    """
    支付订单表
    根据function-table.md中的设计实现
    """
    # 支付状态常量
    STATUS_CREATED = 'created'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (STATUS_CREATED, '已创建'),
        (STATUS_PAID, '成功'),
        (STATUS_FAILED, '失败'),
        (STATUS_REFUNDED, '已退款'),
    ]
    
    # 支付网关常量
    GATEWAY_WECHAT = 'wechat'
    GATEWAY_ALIPAY = 'alipay'
    
    GATEWAY_CHOICES = [
        (GATEWAY_WECHAT, '微信支付'),
        (GATEWAY_ALIPAY, '支付宝'),
    ]
    
    # 字段定义
    id = models.BigAutoField(primary_key=True, help_text='主键ID')
    order_number = models.CharField(max_length=64, unique=True, blank=True, null=True, help_text='平台内部生成的唯一订单号')
    user_id = models.BigIntegerField(help_text='发起支付的用户ID')
    bill_id = models.BigIntegerField(blank=True, null=True, help_text='关联的物业费账单ID（可为空，预留其他支付）')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='支付金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED, help_text='支付状态')
    payment_gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES, blank=True, null=True, help_text='支付网关')
    gateway_order_no = models.CharField(max_length=64, blank=True, null=True, help_text='支付平台返回的交易号')
    created_at = models.DateTimeField(auto_now_add=True, help_text='订单创建时间')
    updated_at = models.DateTimeField(auto_now=True, help_text='订单更新时间')
    paid_at = models.DateTimeField(blank=True, null=True, help_text='支付成功时间')
    
    class Meta:
        db_table = 'payment_orders'
        verbose_name = '支付订单'
        verbose_name_plural = '支付订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'订单 {self.order_number} - {self.get_status_display()}'
    
    def generate_order_number(self):
        """
        生成唯一的订单号
        格式: P + 年月日时分秒 + 6位随机数
        """
        if not self.order_number:
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            random_part = str(uuid.uuid4())[:6].upper()
            self.order_number = f'P{timestamp}{random_part}'
    
    def save(self, *args, **kwargs):
        """
        重写save方法，确保生成订单号
        """
        self.generate_order_number()
        super().save(*args, **kwargs)
