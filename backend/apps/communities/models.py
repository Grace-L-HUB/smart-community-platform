from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
import uuid


class Community(models.Model):
    """小区表"""
    name = models.CharField(_('小区名称'), max_length=100, unique=True)
    address = models.CharField(_('地址'), max_length=200)
    property_phone = models.CharField(_('物业电话'), max_length=20)
    fee_standard = models.DecimalField(
        _('物业费标准'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='元/平米'
    )
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
    id = models.BigIntegerField(_('主键'), primary_key=True)
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

    id = models.BigIntegerField(_('主键'), primary_key=True)
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
    certificate_image = models.CharField(_('房产证照片URL'), max_length=255, blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='approved_houses', null=True, blank=True, verbose_name=_('审核人'))
    approved_at = models.DateTimeField(_('审核时间'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('用户房产绑定')
        verbose_name_plural = _('用户房产绑定')
        unique_together = ('user', 'house')
    
    def __str__(self):
        return f'{self.user.username} - {self.house}'


class PropertyFeeBill(models.Model):
    """物业费账单表"""
    class BillStatus(models.TextChoices):
        PENDING = 'pending', _('待支付')
        PAID = 'paid', _('已支付')
        OVERDUE = 'overdue', _('已逾期')

    id = models.BigIntegerField(_('主键ID'), primary_key=True)
    house_id = models.BigIntegerField(_('关联的房屋ID'))
    billing_period = models.CharField(_('账期'), max_length=7, help_text='格式：YYYY-MM')
    amount = models.DecimalField(_('应缴金额'), max_digits=10, decimal_places=2)
    status = models.CharField(_('状态'), max_length=20, choices=BillStatus.choices, default=BillStatus.PENDING)
    due_date = models.DateField(_('缴费截止日期'))
    paid_at = models.DateTimeField(_('支付成功时间'), blank=True, null=True)
    created_at = models.DateTimeField(_('账单创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('最后更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('物业费账单')
        verbose_name_plural = _('物业费账单')
        unique_together = ('house_id', 'billing_period')
    
    def __str__(self):
        return f'{self.billing_period} 账单 - {self.amount}元'


class VisitorPass(models.Model):
    """访客通行表"""
    class PassStatus(models.TextChoices):
        ACTIVE = 'active', _('有效')
        USED = 'used', _('已使用')
        EXPIRED = 'expired', _('已过期')
        CANCELLED = 'cancelled', _('已取消')

    id = models.BigIntegerField(_('主键ID'), primary_key=True)
    user_id = models.BigIntegerField(_('生成此通行证的居民用户ID'))
    house_id = models.BigIntegerField(_('访问的房产ID'))
    visitor_name = models.CharField(_('访客姓名'), max_length=100)
    visitor_phone = models.CharField(_('访客手机号'), max_length=20)
    pass_code = models.CharField(_('唯一的通行二维码内容'), max_length=32, default=uuid.uuid4)
    valid_from = models.DateTimeField(_('有效期开始时间'))
    valid_to = models.DateTimeField(_('有效期结束时间'))
    status = models.CharField(_('状态'), max_length=20, choices=PassStatus.choices, default=PassStatus.ACTIVE)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('访客通行证')
        verbose_name_plural = _('访客通行证')
    
    def __str__(self):
        return f'{self.visitor_name} 的通行证 - {self.status}'
