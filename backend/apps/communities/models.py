from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Community(models.Model):
    """小区表"""
    name = models.CharField(_('小区名称'), max_length=100, unique=True)
    address = models.CharField(_('地址'), max_length=200)
    property_phone = models.CharField(_('物业电话'), max_length=20)
    fee_standard = models.DecimalField(_('物业费标准'), max_digits=10, decimal_places=2, help_text='元/平米')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('小区')
        verbose_name_plural = _('小区')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Building(models.Model):
    """楼栋表"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='buildings', verbose_name=_('小区'))
    name = models.CharField(_('楼栋名称'), max_length=32)
    unit_count = models.IntegerField(_('单元数'), default=1)
    
    class Meta:
        verbose_name = _('楼栋')
        verbose_name_plural = _('楼栋')
        unique_together = ('community', 'name')
    
    def __str__(self):
        return f'{self.community.name}-{self.name}'


class House(models.Model):
    """房屋表"""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='houses', verbose_name=_('楼栋'))
    unit = models.CharField(_('单元号'), max_length=10)
    number = models.CharField(_('房号'), max_length=10)
    area = models.DecimalField(_('建筑面积'), max_digits=8, decimal_places=2, help_text='平方米')
    owner_name = models.CharField(_('业主姓名'), max_length=64, blank=True, null=True)
    
    class Meta:
        verbose_name = _('房屋')
        verbose_name_plural = _('房屋')
        unique_together = ('building', 'unit', 'number')
    
    def __str__(self):
        return f'{self.building.community.name}-{self.building.name}-{self.unit}-{self.number}'


class UserHouse(models.Model):
    """用户房产绑定表"""
    class RelationshipType(models.TextChoices):
        OWNER = 'owner', _('业主')
        FAMILY = 'family', _('家庭成员')
    
    class StatusType(models.TextChoices):
        PENDING = 'pending', _('待审核')
        APPROVED = 'approved', _('已通过')
        REJECTED = 'rejected', _('已拒绝')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_houses', verbose_name=_('用户'))
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='user_houses', verbose_name=_('房屋'))
    relationship = models.CharField(
        _('关系'), 
        max_length=10, 
        choices=RelationshipType.choices,
        default=RelationshipType.OWNER
    )
    status = models.CharField(
        _('审核状态'), 
        max_length=10, 
        choices=StatusType.choices,
        default=StatusType.PENDING
    )
    certificate_image = models.ImageField(_('房产证照片'), upload_to='certificates/', blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='approved_houses', null=True, blank=True, verbose_name=_('审核人'))
    approved_at = models.DateTimeField(_('审核时间'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('用户房产绑定')
        verbose_name_plural = _('用户房产绑定')
        unique_together = ('user', 'house')
    
    def __str__(self):
        return f'{self.user.username} - {self.house}'
