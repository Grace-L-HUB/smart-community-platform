from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """消息通知表"""
    class NotificationType(models.TextChoices):
        WORK_ORDER = 'work_order', _('工单通知')
        ANNOUNCEMENT = 'announcement', _('公告通知')
        MERCHANT_POST = 'merchant_post', _('商户动态通知')
        SYSTEM = 'system', _('系统通知')
    
    class SendVia(models.TextChoices):
        APP = 'app', _('应用内')
        SMS = 'sms', _('短信')
        WECHAT = 'wechat', _('微信')
    
    class SendStatus(models.TextChoices):
        PENDING = 'pending', _('待发送')
        SENT = 'sent', _('已发送')
        FAILED = 'failed', _('发送失败')
    
    id = models.BigIntegerField(_('主键'), primary_key=True)
    user_id = models.BigIntegerField(_('接收用户ID'))
    title = models.CharField(_('消息标题'), max_length=200)
    notification_type = models.CharField(
        _('消息种类'), 
        max_length=20, 
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    content = models.TextField(_('消息内容'))
    related_id = models.BigIntegerField(_('关联业务ID'), null=True, blank=True)
    is_read = models.BooleanField(_('是否已读'), default=False)
    sent_via = models.CharField(_('发送渠道'), max_length=20, choices=SendVia.choices, default=SendVia.APP)
    sent_status = models.CharField(_('发送状态'), max_length=20, choices=SendStatus.choices, default=SendStatus.PENDING)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('消息通知')
        verbose_name_plural = _('消息通知')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_notification_type_display()} - {self.title}'
