from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """用户角色枚举"""
    ADMIN = 'admin', _('管理员')
    PROPERTY_STAFF = 'property_staff', _('物业人员')
    RESIDENT = 'resident', _('业主')
    MERCHANT = 'merchant', _('商家')


class User(AbstractUser):
    """自定义用户模型，扩展Django默认用户模型"""
    # 基本信息扩展
    phone = models.CharField(_('手机号码'), max_length=11, blank=True, null=True, unique=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    
    # 角色信息
    role = models.CharField(
        _('用户角色'),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.RESIDENT,
    )
    
    # 附加信息
    id_card = models.CharField(_('身份证号'), max_length=18, blank=True, null=True)
    emergency_contact = models.CharField(_('紧急联系人'), max_length=20, blank=True, null=True)
    emergency_phone = models.CharField(_('紧急联系电话'), max_length=11, blank=True, null=True)
    
    # 状态信息
    is_verified = models.BooleanField(_('是否已实名认证'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username or self.phone or f'用户-{self.id}'


class Address(models.Model):
    """用户地址信息"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name=_('用户'))
    province = models.CharField(_('省份'), max_length=50)
    city = models.CharField(_('城市'), max_length=50)
    district = models.CharField(_('区县'), max_length=50)
    detail_address = models.CharField(_('详细地址'), max_length=200)
    is_default = models.BooleanField(_('是否默认地址'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('用户地址')
        verbose_name_plural = _('用户地址')
    
    def __str__(self):
        return f'{self.province}{self.city}{self.district}{self.detail_address}'


class UserProfile(models.Model):
    """用户详细资料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('用户'))
    real_name = models.CharField(_('真实姓名'), max_length=20, blank=True, null=True)
    gender = models.CharField(
        _('性别'),
        max_length=10,
        choices=(('male', _('男')), ('female', _('女')), ('other', _('其他'))),
        blank=True,
        null=True
    )
    birthday = models.DateField(_('出生日期'), blank=True, null=True)
    bio = models.TextField(_('个人简介'), blank=True, null=True, max_length=200)
    
    class Meta:
        verbose_name = _('用户资料')
        verbose_name_plural = _('用户资料')
    
    def __str__(self):
        return f'{self.user.username}的详细资料'
