from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserRole(models.Model):
    """角色权限表，符合function-table.md设计"""
    class RoleType(models.TextChoices):
        PROPERTY = 'property', _('物业')
        MERCHANT = 'merchant', _('商户')
        RESIDENT = 'resident', _('居民')
    
    id = models.IntegerField(_('主键'), primary_key=True)
    name = models.CharField(_('角色名（admin,客服,维修工）'), max_length=32, unique=True)
    role_type = models.CharField(
        _('角色类型'),
        max_length=20,
        choices=RoleType.choices
    )
    permissions = models.JSONField(_('权限列表（菜单+操作）'), default=dict, blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('角色权限')
        verbose_name_plural = _('角色权限')
    
    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, phone, password=None, **extra_fields):
        """创建普通用户"""
        if not phone:
            raise ValueError('必须提供手机号')
        user = self.model(username=username, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """用户表，符合function-table.md设计"""
    # 微信相关字段
    id = models.BigAutoField(_('主键'), primary_key=True)
    openid = models.CharField(_('微信OpenID'), max_length=64, blank=True, null=True, unique=True)
    
    # 账号信息
    username = models.CharField(_('用户名'), max_length=64, blank=True, null=True, unique=True)
    phone = models.CharField(_('手机号'), max_length=20, blank=True, null=True, unique=True)
    avatar_url = models.CharField(_('头像URL'), max_length=255, blank=True, null=True)
    
    # 角色关联
    role_id = models.IntegerField(_('角色id'), blank=True, null=True)
    
    # Django认证必需字段
    is_active = models.BooleanField(_('是否激活'), default=False)
    is_staff = models.BooleanField(_('是否是员工'), default=False)
    is_superuser = models.BooleanField(_('是否是超级用户'), default=False)
    
    # 其他状态信息
    is_blacklisted = models.BooleanField(_('是否黑名单用户'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    is_deleted = models.BooleanField(_('是否删除'), default=False)
    deleted_at = models.DateTimeField(_('删除时间'), blank=True, null=True)
    
    # Django用户模型必需的属性
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-created_at']
    

    
    def __str__(self):
        return self.username or self.phone or f'用户-{self.id}'
