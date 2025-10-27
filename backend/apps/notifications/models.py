from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Notification(models.Model):
    """通知表"""
    class NotificationType(models.TextChoices):
        SYSTEM = 'system', _('系统通知')
        ORDER = 'order', _('订单通知')
        WORK_ORDER = 'work_order', _('工单通知')
        ANNOUNCEMENT = 'announcement', _('公告通知')
        ACTIVITY = 'activity', _('活动通知')
        SECURITY = 'security', _('安全提醒')
        OTHER = 'other', _('其他通知')
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('接收用户'))
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications', verbose_name=_('发送用户'))
    type = models.CharField(
        _('通知类型'), 
        max_length=20, 
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(_('通知标题'), max_length=200)
    content = models.TextField(_('通知内容'))
    is_read = models.BooleanField(_('是否已读'), default=False)
    read_at = models.DateTimeField(_('阅读时间'), null=True, blank=True)
    action_url = models.URLField(_('跳转链接'), null=True, blank=True)
    related_id = models.IntegerField(_('关联ID'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('通知')
        verbose_name_plural = _('通知')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_type_display()} - {self.title}'
