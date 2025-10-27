from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.communities.models import Community


class ServiceCategory(models.Model):
    """服务类别表"""
    name = models.CharField(_('类别名称'), max_length=50)
    description = models.TextField(_('类别描述'), null=True, blank=True)
    icon = models.URLField(_('图标URL'), null=True, blank=True)
    sort_order = models.IntegerField(_('排序'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('服务类别')
        verbose_name_plural = _('服务类别')
        ordering = ['sort_order']
    
    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    """服务提供商表"""
    name = models.CharField(_('提供商名称'), max_length=100)
    contact_person = models.CharField(_('联系人'), max_length=50)
    contact_phone = models.CharField(_('联系电话'), max_length=20)
    email = models.EmailField(_('邮箱'), null=True, blank=True)
    description = models.TextField(_('提供商描述'), null=True, blank=True)
    logo = models.URLField(_('提供商logo'), null=True, blank=True)
    rating = models.DecimalField(_('评分'), max_digits=2, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('服务提供商')
        verbose_name_plural = _('服务提供商')
    
    def __str__(self):
        return self.name


class Service(models.Model):
    """服务表"""
    class ServiceStatus(models.TextChoices):
        ACTIVE = 'active', _('启用')
        INACTIVE = 'inactive', _('禁用')
    
    name = models.CharField(_('服务名称'), max_length=100)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name=_('服务类别'))
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services', verbose_name=_('服务提供商'))
    description = models.TextField(_('服务描述'))
    price = models.DecimalField(_('服务价格'), max_digits=8, decimal_places=2)
    unit = models.CharField(_('计价单位'), max_length=20, default='次')
    duration = models.IntegerField(_('预计时长（分钟）'), null=True, blank=True)
    cover_image = models.URLField(_('封面图片'), null=True, blank=True)
    images = models.JSONField(_('图片列表'), null=True, blank=True)
    is_popular = models.BooleanField(_('是否热门'), default=False)
    status = models.CharField(
        _('服务状态'), 
        max_length=20, 
        choices=ServiceStatus.choices,
        default=ServiceStatus.ACTIVE
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('服务')
        verbose_name_plural = _('服务')
    
    def __str__(self):
        return self.name


class ServiceOrder(models.Model):
    """服务订单表"""
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('待支付')
        PAID = 'paid', _('已支付')
        SCHEDULED = 'scheduled', _('已预约')
        PROCESSING = 'processing', _('进行中')
        COMPLETED = 'completed', _('已完成')
        CANCELLED = 'cancelled', _('已取消')
        REFUNDED = 'refunded', _('已退款')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_orders', verbose_name=_('用户'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders', verbose_name=_('服务'))
    quantity = models.IntegerField(_('数量'), default=1)
    total_amount = models.DecimalField(_('订单总额'), max_digits=8, decimal_places=2)
    scheduled_at = models.DateTimeField(_('预约时间'), null=True, blank=True)
    service_address = models.CharField(_('服务地址'), max_length=200)
    contact_name = models.CharField(_('联系人'), max_length=50)
    contact_phone = models.CharField(_('联系电话'), max_length=20)
    remarks = models.TextField(_('备注'), null=True, blank=True)
    status = models.CharField(
        _('订单状态'), 
        max_length=20, 
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    payment_time = models.DateTimeField(_('支付时间'), null=True, blank=True)
    payment_method = models.CharField(_('支付方式'), max_length=20, null=True, blank=True)
    payment_no = models.CharField(_('支付单号'), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('服务订单')
        verbose_name_plural = _('服务订单')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'服务订单 #{self.id} - {self.service.name}'


class ServiceReview(models.Model):
    """服务评价表"""
    service_order = models.OneToOneField(ServiceOrder, on_delete=models.CASCADE, related_name='review', verbose_name=_('服务订单'))
    rating = models.IntegerField(_('评分'), choices=[(i, str(i)) for i in range(1, 6)])
    content = models.TextField(_('评价内容'), null=True, blank=True)
    images = models.JSONField(_('评价图片'), null=True, blank=True)
    created_at = models.DateTimeField(_('评价时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('服务评价')
        verbose_name_plural = _('服务评价')
    
    def __str__(self):
        return f'服务评价 #{self.service_order.id}'
