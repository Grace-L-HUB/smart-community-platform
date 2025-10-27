from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.communities.models import Community


class Merchant(models.Model):
    """商户表"""
    class MerchantStatus(models.TextChoices):
        PENDING = 'pending', _('待审核')
        APPROVED = 'approved', _('已通过')
        REJECTED = 'rejected', _('已拒绝')
        SUSPENDED = 'suspended', _('已暂停')
    
    # 基本信息
    name = models.CharField(_('商户名称'), max_length=100)
    contact_person = models.CharField(_('联系人'), max_length=50)
    contact_phone = models.CharField(_('联系电话'), max_length=20)
    email = models.EmailField(_('邮箱'), null=True, blank=True)
    business_license = models.CharField(_('营业执照号'), max_length=50, null=True, blank=True)
    logo = models.URLField(_('商户logo'), null=True, blank=True)
    description = models.TextField(_('商户描述'), null=True, blank=True)
    address = models.CharField(_('商户地址'), max_length=200)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='merchants', verbose_name=_('所属小区'))
    
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
    
    # 其他信息
    business_hours = models.CharField(_('营业时间'), max_length=100, null=True, blank=True)
    status = models.CharField(
        _('商户状态'), 
        max_length=20, 
        choices=MerchantStatus.choices,
        default=MerchantStatus.PENDING
    )
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_merchants', verbose_name=_('审核人'))
    approved_at = models.DateTimeField(_('审核时间'), null=True, blank=True)
    rejection_reason = models.TextField(_('拒绝原因'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    # 关联用户（用于登录）
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='merchant', verbose_name=_('关联用户'))
    
    class Meta:
        verbose_name = _('商户')
        verbose_name_plural = _('商户')
    
    def __str__(self):
        return self.name


class MerchantService(models.Model):
    """商户服务表（整合原services应用的Service）"""
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='services', verbose_name=_('商户'))
    name = models.CharField(_('服务名称'), max_length=100)
    description = models.TextField(_('服务描述'), null=True, blank=True)
    price = models.DecimalField(_('服务价格'), max_digits=8, decimal_places=2, default=0.00)
    unit = models.CharField(_('计价单位'), max_length=20, default='次')
    duration = models.IntegerField(_('预计时长（分钟）'), null=True, blank=True)
    images = models.JSONField(_('服务图片'), null=True, blank=True)
    cover_image = models.URLField(_('封面图片'), null=True, blank=True)
    is_active = models.BooleanField(_('是否启用'), default=True)
    is_popular = models.BooleanField(_('是否热门'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('商户服务')
        verbose_name_plural = _('商户服务')
    
    def __str__(self):
        return f'{self.merchant.name} - {self.name}'


class MerchantOrder(models.Model):
    """商户服务订单表（整合原services应用的ServiceOrder）"""
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('待支付')
        PAID = 'paid', _('已支付')
        SCHEDULED = 'scheduled', _('已预约')
        PROCESSING = 'processing', _('处理中')
        COMPLETED = 'completed', _('已完成')
        CANCELLED = 'cancelled', _('已取消')
        REFUNDED = 'refunded', _('已退款')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='merchant_orders', verbose_name=_('用户'))
    merchant_service = models.ForeignKey(MerchantService, on_delete=models.CASCADE, related_name='orders', verbose_name=_('服务'))
    quantity = models.IntegerField(_('数量'), default=1)
    total_amount = models.DecimalField(_('订单总额'), max_digits=8, decimal_places=2)
    status = models.CharField(
        _('订单状态'), 
        max_length=20, 
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    scheduled_at = models.DateTimeField(_('预约时间'), null=True, blank=True)
    service_address = models.CharField(_('服务地址'), max_length=200, null=True, blank=True)
    contact_name = models.CharField(_('联系人'), max_length=50, null=True, blank=True)
    contact_phone = models.CharField(_('联系电话'), max_length=20, null=True, blank=True)
    payment_time = models.DateTimeField(_('支付时间'), null=True, blank=True)
    payment_method = models.CharField(_('支付方式'), max_length=20, null=True, blank=True)
    payment_no = models.CharField(_('支付单号'), max_length=100, null=True, blank=True)
    remarks = models.TextField(_('备注'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('商户订单')
        verbose_name_plural = _('商户订单')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'订单 #{self.id} - {self.merchant_service.name}'


class ServiceReview(models.Model):
    """服务评价表（来自原services应用）"""
    merchant_order = models.OneToOneField(MerchantOrder, on_delete=models.CASCADE, related_name='review', verbose_name=_('订单'))
    rating = models.IntegerField(_('评分'), choices=[(i, str(i)) for i in range(1, 6)])
    content = models.TextField(_('评价内容'), null=True, blank=True)
    images = models.JSONField(_('评价图片'), null=True, blank=True)
    created_at = models.DateTimeField(_('评价时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('服务评价')
        verbose_name_plural = _('服务评价')
    
    def __str__(self):
        return f'服务评价 #{self.merchant_order.id}'


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
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='posts', verbose_name=_('商户'))
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('用户'))
    target_type = models.CharField(_('收藏类型'), max_length=20, choices=TargetType.choices)
    target_id = models.BigIntegerField(_('收藏目标ID'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('用户收藏')
        verbose_name_plural = _('用户收藏')
        unique_together = ('user', 'target_type', 'target_id')
    
    def __str__(self):
        return f'{self.user.username}收藏{self.get_target_type_display()}{self.target_id}'


class PostLike(models.Model):
    """动态点赞表（新增，来自function-table.md）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes', verbose_name=_('用户'))
    post = models.ForeignKey(MerchantPost, on_delete=models.CASCADE, related_name='likes', verbose_name=_('动态'))
    created_at = models.DateTimeField(_('点赞时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('动态点赞')
        verbose_name_plural = _('动态点赞')
        unique_together = ('user', 'post')
    
    def __str__(self):
        return f'{self.user.username}点赞{self.post.title}'


class PostComment(models.Model):
    """动态评论表（新增，来自function-table.md）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_comments', verbose_name=_('用户'))
    post = models.ForeignKey(MerchantPost, on_delete=models.CASCADE, related_name='comments', verbose_name=_('动态'))
    content = models.TextField(_('评论内容'))
    created_at = models.DateTimeField(_('评论时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('动态评论')
        verbose_name_plural = _('动态评论')
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.user.username}评论{self.post.title}'


class MerchantStat(models.Model):
    """商户统计表（新增，来自function-table.md）"""
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='stats', verbose_name=_('商户'))
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
        return f'{self.merchant.name} {self.date} 统计'
