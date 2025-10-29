from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Merchant(models.Model):
    """商户表"""
    class MerchantStatus(models.TextChoices):
        PENDING = 'pending', _('待审核')
        APPROVED = 'approved', _('已通过')
        REJECTED = 'rejected', _('已拒绝')
    
    id = models.BigIntegerField(_('主键'), primary_key=True)
    user_id = models.BigIntegerField(_('关联用户ID'), blank=True, null=True)
    name = models.CharField(_('商户名称'), max_length=100)
    
    # 服务分类（整合自function-table.md）
    class ServiceCategory(models.TextChoices):
        REPAIR_SERVICE = 'REPAIR_SERVICE', _('维修服务')
        LIFE_SERVICE = 'LIFE_SERVICE', _('生活服务')
        RETAIL_STORE = 'RETAIL_STORE', _('商超零售')
        FOOD_BEVERAGE = 'FOOD_BEVERAGE', _('餐饮')
    
    service_categories = models.CharField(
        _('服务分类'),
        max_length=50,
        choices=ServiceCategory.choices,
        null=True,
        blank=True
    )
    
    address = models.CharField(_('地址'), max_length=200)
    phone = models.CharField(_('联系电话'), max_length=20)
    business_hours = models.CharField(_('营业时间'), max_length=100)
    description = models.TextField(_('服务介绍'))
    images = models.JSONField(_('门店照片URL列表'), null=True, blank=True)
    status = models.CharField(
        _('入驻状态'), 
        max_length=20, 
        choices=MerchantStatus.choices,
        default=MerchantStatus.PENDING
    )
    approved_by = models.BigIntegerField(_('审核人ID'), null=True, blank=True)
    approved_at = models.DateTimeField(_('审核时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('商户')
        verbose_name_plural = _('商户')
    
    def __str__(self):
        return self.name


# 移除不在function-table.md中的MerchantService、MerchantOrder和ServiceReview表


class Coupon(models.Model):
    """优惠券表（新增，来自function-table.md）"""
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='coupons', verbose_name=_('商户'))
    title = models.CharField(_('优惠标题'), max_length=100)
    description = models.TextField(_('优惠内容'))
    image_url = models.URLField(_('优惠图片'), null=True, blank=True)
    start_date = models.DateField(_('开始日期'))
    end_date = models.DateField(_('结束日期'))
    view_count = models.IntegerField(_('查看次数'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('优惠券')
        verbose_name_plural = _('优惠券')
    
    def __str__(self):
        return f'{self.merchant.name} - {self.title}'


class MerchantPost(models.Model):
    """商户动态表（新增，来自function-table.md）"""
    id = models.BigIntegerField(_('主键'), primary_key=True)
    merchant_id = models.BigIntegerField(_('商户ID'))
    title = models.CharField(_('动态标题'), max_length=200)
    content = models.TextField(_('动态内容'))
    images = models.JSONField(_('图片列表'), null=True, blank=True)
    like_count = models.IntegerField(_('点赞数'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('商户动态')
        verbose_name_plural = _('商户动态')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class UserFavorite(models.Model):
    """用户收藏表（新增，来自function-table.md）"""
    class TargetType(models.TextChoices):
        MERCHANT = 'merchant', _('商户')
        COUPON = 'coupon', _('优惠券')
    
    id = models.BigIntegerField(_('主键'), primary_key=True)
    user_id = models.BigIntegerField(_('用户ID'))
    target_type = models.CharField(_('收藏类型'), max_length=20, choices=TargetType.choices)
    target_id = models.BigIntegerField(_('收藏目标ID'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('用户收藏')
        verbose_name_plural = _('用户收藏')
        unique_together = ('user_id', 'target_type', 'target_id')
    
    
    def __str__(self):
        return f'用户{self.user_id}收藏{self.get_target_type_display()}{self.target_id}'


class PostLike(models.Model):
    """动态点赞表（新增，来自function-table.md）"""
    id = models.BigIntegerField(_('主键'), primary_key=True)
    user_id = models.BigIntegerField(_('用户ID'))
    post_id = models.BigIntegerField(_('动态ID'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('动态点赞')
        verbose_name_plural = _('动态点赞')
        unique_together = ('user_id', 'post_id')
    
    def __str__(self):
        return f'用户{self.user_id}点赞动态{self.post_id}'


class PostComment(models.Model):
    """动态评论表（新增，来自function-table.md）"""
    id = models.BigIntegerField(_('主键'), primary_key=True)
    user_id = models.BigIntegerField(_('用户ID'))
    post_id = models.BigIntegerField(_('动态ID'))
    content = models.TextField(_('评论内容'))
    created_at = models.DateTimeField(_('评论时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('动态评论')
        verbose_name_plural = _('动态评论')
        ordering = ['created_at']
    
    def __str__(self):
        return f'评论 #{self.id} - 动态 {self.post_id}'

# 移除不在function-table.md中的MerchantStat表（已移至data_statistics应用）
