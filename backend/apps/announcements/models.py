from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.communities.models import Community, Building, House


class Announcement(models.Model):
    """公告表"""
    class AnnouncementType(models.TextChoices):
        EMERGENCY = 'emergency', _('紧急通知')
        ACTIVITY = 'activity', _('活动通知')
        NORMAL = 'normal', _('普通公告')
    
    class TargetType(models.TextChoices):
        ALL = 'all', _('全部居民')
        BUILDING = 'building', _('指定楼栋')
        HOUSE = 'house', _('指定房屋')
    
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='announcements', verbose_name=_('小区'))
    title = models.CharField(_('标题'), max_length=200)
    content = models.TextField(_('内容'))
    type = models.CharField(
        _('类型'), 
        max_length=20, 
        choices=AnnouncementType.choices,
        default=AnnouncementType.NORMAL
    )
    target_type = models.CharField(
        _('推送范围类型'), 
        max_length=20, 
        choices=TargetType.choices,
        default=TargetType.ALL
    )
    target_ids = models.JSONField(_('目标ID列表'), null=True, blank=True)
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='published_announcements', verbose_name=_('发布人'))
    is_published = models.BooleanField(_('是否发布'), default=False)
    published_at = models.DateTimeField(_('发布时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('公告')
        verbose_name_plural = _('公告')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class AnnouncementRead(models.Model):
    """公告已读表"""
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='reads', verbose_name=_('公告'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_announcements', verbose_name=_('用户'))
    read_at = models.DateTimeField(_('阅读时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('公告已读')
        verbose_name_plural = _('公告已读')
        unique_together = ('announcement', 'user')
    
    def __str__(self):
        return f'{self.user.username} - {self.announcement.title}'
