from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.communities.models import House


class WorkOrder(models.Model):
    """工单表"""
    class UrgencyType(models.TextChoices):
        HIGH = 'high', _('紧急')
        MEDIUM = 'medium', _('一般')
        LOW = 'low', _('低')
    
    class StatusType(models.TextChoices):
        PENDING = 'pending', _('待受理')
        PROCESSING = 'processing', _('处理中')
        COMPLETED = 'completed', _('已完成')
        REJECTED = 'rejected', _('已驳回')
        WAITING_RESIDENT = 'waiting_resident', _('待居民补充')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_orders', verbose_name=_('报修用户'))
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='work_orders', verbose_name=_('房产'))
    type = models.CharField(_('报修类型'), max_length=32)
    description = models.TextField(_('问题描述'))
    images = models.JSONField(_('图片URL列表'), null=True, blank=True)
    urgency = models.CharField(
        _('紧急程度'), 
        max_length=20, 
        choices=UrgencyType.choices,
        default=UrgencyType.MEDIUM
    )
    status = models.CharField(
        _('工单状态'), 
        max_length=20, 
        choices=StatusType.choices,
        default=StatusType.PENDING
    )
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', verbose_name=_('指派给'))
    assigned_at = models.DateTimeField(_('指派时间'), null=True, blank=True)
    expected_finish_at = models.DateTimeField(_('预计完成时间'), null=True, blank=True)
    completed_at = models.DateTimeField(_('实际完成时间'), null=True, blank=True)
    reject_reason = models.TextField(_('驳回原因'), null=True, blank=True)
    resident_supplement = models.TextField(_('居民补充信息'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('工单')
        verbose_name_plural = _('工单')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'工单 #{self.id} - {self.user.username}'


class WorkOrderComment(models.Model):
    """工单留言表"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='comments', verbose_name=_('工单'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_order_comments', verbose_name=_('留言用户'))
    content = models.TextField(_('留言内容'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('工单留言')
        verbose_name_plural = _('工单留言')
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.work_order.id}'


class WorkOrderRating(models.Model):
    """工单评价表"""
    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE, related_name='rating', verbose_name=_('工单'))
    service_rating = models.IntegerField(_('服务质量'), choices=[(i, str(i)) for i in range(1, 6)])
    efficiency_rating = models.IntegerField(_('处理效率'), choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(_('评价内容'), null=True, blank=True)
    created_at = models.DateTimeField(_('评价时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('工单评价')
        verbose_name_plural = _('工单评价')
    
    def __str__(self):
        return f'工单评价 #{self.work_order.id}'
