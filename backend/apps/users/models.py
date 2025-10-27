from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password


class UserRole(models.Model):
    """角色权限表"""
    class RoleType(models.TextChoices):
        PROPERTY = 'property', _('物业角色')
        MERCHANT = 'merchant', _('商户角色')
        RESIDENT = 'resident', _('居民角色')
    
    name = models.CharField(_('角色名'), max_length=32, unique=True)  # admin, 客服, 维修工
    role_type = models.CharField(
        _('角色类型'),
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.RESIDENT
    )
    permissions = models.JSONField(_('权限列表'), default=dict)  # 菜单+操作权限
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('角色权限')
        verbose_name_plural = _('角色权限')
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """用户表，符合function-table.md设计"""
    # 微信相关字段
    openid = models.CharField(_('微信OpenID'), max_length=64, blank=True, null=True, unique=True)
    
    # 账号信息
    username = models.CharField(_('用户名'), max_length=64, blank=True, null=True, unique=True)
    password = models.CharField(_('密码哈希'), max_length=255, blank=True, null=True)
    phone = models.CharField(_('手机号'), max_length=20, blank=True, null=True, unique=True)
    avatar_url = models.CharField(_('头像URL'), max_length=255, blank=True, null=True)
    
    # 角色关联
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, related_name='users', verbose_name=_('角色'))
    
    # 状态信息
    is_active = models.BooleanField(_('是否激活'), default=False)
    is_deleted = models.BooleanField(_('是否删除'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    deleted_at = models.DateTimeField(_('删除时间'), blank=True, null=True)
    
    # 保留AbstractUser的字段但允许为空
    email = models.EmailField(_('邮箱地址'), blank=True, null=True)
    first_name = models.CharField(_('名字'), max_length=30, blank=True)
    last_name = models.CharField(_('姓氏'), max_length=150, blank=True)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-created_at']
    
    def set_password(self, raw_password):
        """设置密码，进行哈希处理"""
        self.password = make_password(raw_password)
    
    def __str__(self):
        return self.username or self.phone or f'用户-{self.id}'


class UserProfile(models.Model):
    """用户详细资料，保留以兼容现有功能"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('用户'))
    real_name = models.CharField(_('真实姓名'), max_length=20, blank=True, null=True)
    id_card = models.CharField(_('身份证号'), max_length=18, blank=True, null=True)
    gender = models.CharField(
        _('性别'),
        max_length=10,
        choices=(('male', _('男')), ('female', _('女')), ('other', _('其他'))),
        blank=True,
        null=True
    )
    birthday = models.DateField(_('出生日期'), blank=True, null=True)
    emergency_contact = models.CharField(_('紧急联系人'), max_length=20, blank=True, null=True)
    emergency_phone = models.CharField(_('紧急联系电话'), max_length=11, blank=True, null=True)
    is_verified = models.BooleanField(_('是否已实名认证'), default=False)
    
    class Meta:
        verbose_name = _('用户资料')
        verbose_name_plural = _('用户资料')
    
    def __str__(self):
        return f'{self.user.username}的详细资料'
