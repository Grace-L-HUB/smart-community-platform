from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.communities.models import Community, House
from apps.work_orders.models import WorkOrder


class VisitRecord(models.Model):
    """访客记录表"""
    class VisitPurpose(models.TextChoices):
        FRIEND = 'friend', _('拜访亲友')
        WORK = 'work', _('工作访问')
        DELIVERY = 'delivery', _('快递配送')
        OTHER = 'other', _('其他')
    
    visitor_name = models.CharField(_('访客姓名'), max_length=50)
    visitor_phone = models.CharField(_('访客电话'), max_length=20)
    id_card_number = models.CharField(_('身份证号'), max_length=18)
    visit_purpose = models.CharField(
        _('访问目的'), 
        max_length=20, 
        choices=VisitPurpose.choices,
        default=VisitPurpose.OTHER
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='visit_records', verbose_name=_('小区'))
    target_house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='visit_records', verbose_name=_('目标房屋'))
    host_name = models.CharField(_('被访人姓名'), max_length=50)
    host_phone = models.CharField(_('被访人电话'), max_length=20)
    visit_time = models.DateTimeField(_('到访时间'))
    leave_time = models.DateTimeField(_('离开时间'), null=True, blank=True)
    vehicle_info = models.CharField(_('车辆信息'), max_length=100, null=True, blank=True)
    gate_entered = models.CharField(_('进入门岗'), max_length=50)
    gate_left = models.CharField(_('离开门岗'), max_length=50, null=True, blank=True)
    image_url = models.URLField(_('访客照片'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('访客记录')
        verbose_name_plural = _('访客记录')
        ordering = ['-visit_time']
    
    def __str__(self):
        return f'{self.visitor_name} - {self.community.name}'


class SecurityIncident(models.Model):
    """安全事件表"""
    class IncidentType(models.TextChoices):
        THEFT = 'theft', _('盗窃')
        FIGHT = 'fight', _('打架斗殴')
        FIRE = 'fire', _('火灾')
        ACCIDENT = 'accident', _('意外伤害')
        VIOLENCE = 'violence', _('暴力事件')
        OTHER = 'other', _('其他')
    
    class IncidentSeverity(models.TextChoices):
        CRITICAL = 'critical', _('严重')
        HIGH = 'high', _('高')
        MEDIUM = 'medium', _('中')
        LOW = 'low', _('低')
    
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='security_incidents', verbose_name=_('小区'))
    location = models.CharField(_('事件地点'), max_length=200)
    incident_type = models.CharField(
        _('事件类型'), 
        max_length=20, 
        choices=IncidentType.choices,
        default=IncidentType.OTHER
    )
    severity = models.CharField(
        _('严重程度'), 
        max_length=20, 
        choices=IncidentSeverity.choices,
        default=IncidentSeverity.MEDIUM
    )
    description = models.TextField(_('事件描述'))
    occurred_at = models.DateTimeField(_('发生时间'))
    reported_at = models.DateTimeField(_('上报时间'), auto_now_add=True)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_incidents', verbose_name=_('上报人'))
    is_handled = models.BooleanField(_('是否处理'), default=False)
    handling_details = models.TextField(_('处理详情'), null=True, blank=True)
    handled_at = models.DateTimeField(_('处理完成时间'), null=True, blank=True)
    images = models.JSONField(_('现场图片'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('安全事件')
        verbose_name_plural = _('安全事件')
        ordering = ['-occurred_at']
    
    def __str__(self):
        return f'{self.get_incident_type_display()} - {self.community.name}'
