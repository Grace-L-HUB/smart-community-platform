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
    
    id = models.BigIntegerField(_('主键'), primary_key=True)
    user_id = models.BigIntegerField(_('报修用户ID'))
    house_id = models.BigIntegerField(_('房产ID'))
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
    assigned_to = models.BigIntegerField(_('指派给（维修工ID）'), null=True, blank=True)
    assigned_at = models.DateTimeField(_('指派时间'), null=True, blank=True)
    expected_finish_at = models.DateTimeField(_('预计完成时间'), null=True, blank=True)
    completed_at = models.DateTimeField(_('实际完成时间'), null=True, blank=True)
    warning_time = models.DateTimeField(_('预警触发时间'), null=True, blank=True)
    reject_reason = models.TextField(_('驳回原因'), null=True, blank=True)
    resident_supplement = models.TextField(_('居民补充信息'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('工单')
        verbose_name_plural = _('工单')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'工单 #{self.id}'


class WorkOrderComment(models.Model):
    """工单留言表"""
    id = models.BigIntegerField(_('主键'), primary_key=True)
    work_order_id = models.BigIntegerField(_('工单ID'))
    user_id = models.BigIntegerField(_('留言用户ID'))
    content = models.TextField(_('留言内容'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('工单留言')
        verbose_name_plural = _('工单留言')
        ordering = ['created_at']
    
    def __str__(self):
        return f'留言 #{self.id} - 工单 {self.work_order_id}'


class WorkOrderRating(models.Model):
    """工单评价表"""
    id = models.BigIntegerField(_('主键'), primary_key=True)
    work_order_id = models.BigIntegerField(_('工单ID'), unique=True)
    service_rating = models.IntegerField(_('服务质量（1-5）'), choices=[(i, str(i)) for i in range(1, 6)])
    efficiency_rating = models.IntegerField(_('处理效率（1-5）'), choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(_('评价内容'), null=True, blank=True)
    created_at = models.DateTimeField(_('评价时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('工单评价')
        verbose_name_plural = _('工单评价')
    
    def __str__(self):
        return f'工单评价 #{self.work_order_id}'


class Complaint(models.Model):
    """投诉建议表"""
    class ComplaintStatus(models.TextChoices):
        SUBMITTED = 'submitted', _('已提交')
        PROCESSING = 'processing', _('处理中')
        RESOLVED = 'resolved', _('已解决')
        REJECTED = 'rejected', _('已驳回')
    
    id = models.BigIntegerField(_('主键ID'), primary_key=True)
    user_id = models.BigIntegerField(_('投诉用户ID'))
    house_id = models.BigIntegerField(_('关联的房产ID'))
    type = models.CharField(_('投诉类型'), max_length=50)
    title = models.CharField(_('投诉标题'), max_length=255)
    content = models.TextField(_('投诉详细内容'))
    image_urls = models.JSONField(_('投诉图片URL数组'), null=True, blank=True)
    status = models.CharField(_('状态'), max_length=20, choices=ComplaintStatus.choices, default=ComplaintStatus.SUBMITTED)
    submitted_at = models.DateTimeField(_('提交时间'), auto_now_add=True)
    processed_at = models.DateTimeField(_('处理时间'), null=True, blank=True)
    processor_id = models.BigIntegerField(_('处理人员ID（物业员工）'), null=True, blank=True)
    process_remark = models.TextField(_('处理备注'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('投诉建议')
        verbose_name_plural = _('投诉建议')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f'投诉 #{self.id} - {self.title}'
