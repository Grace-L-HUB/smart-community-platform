from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.merchants.models import Merchant


class MerchantStats(models.Model):
    """商户统计表"""
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='statistics', verbose_name=_('商户'))
    date = models.DateField(_('统计日期'))
    page_views = models.IntegerField(_('页面访问量'), default=0)
    favorite_count = models.IntegerField(_('收藏次数'), default=0)
    coupon_views = models.IntegerField(_('优惠券查看次数'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('商户统计')
        verbose_name_plural = _('商户统计')
        unique_together = ('merchant', 'date')
    
    def __str__(self):
        return f'{self.merchant.name} - {self.date}'


class SystemLog(models.Model):
    """系统日志表"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs', verbose_name=_('操作用户'))
    action = models.CharField(_('操作描述'), max_length=100)
    resource_type = models.CharField(_('资源类型'), max_length=50)
    resource_id = models.BigIntegerField(_('资源ID'), null=True, blank=True)
    ip_address = models.CharField(_('IP地址'), max_length=45)
    user_agent = models.TextField(_('用户代理'))
    created_at = models.DateTimeField(_('操作时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('系统日志')
        verbose_name_plural = _('系统日志')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.action} - {self.created_at}'
