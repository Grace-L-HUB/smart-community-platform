from django.contrib import admin
from .models import Community, Building, House, UserHouse, PropertyFeeBill, VisitorPass


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    """小区管理界面"""
    list_display = ['name', 'address', 'property_phone', 'fee_standard', 'created_at']
    search_fields = ['name', 'address']
    list_filter = ['created_at']
    ordering = ['-created_at']


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    """楼栋管理界面"""
    list_display = ['name', 'community', 'unit_count']
    search_fields = ['name', 'community__name']
    list_filter = ['community', 'unit_count']
    ordering = ['community', 'name']


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    """房屋管理界面"""
    list_display = ['id', 'building', 'unit', 'number', 'area', 'owner_name']
    search_fields = ['unit', 'number', 'owner_name', 'building__name', 'building__community__name']
    list_filter = ['building__community', 'building']
    ordering = ['building', 'unit', 'number']


@admin.register(UserHouse)
class UserHouseAdmin(admin.ModelAdmin):
    """用户房产绑定管理界面"""
    list_display = ['id', 'user', 'house', 'relationship', 'status', 'approved_by', 'approved_at']
    search_fields = ['user__username', 'user__phone', 'house__unit', 'house__number']
    list_filter = ['status', 'relationship', 'approved_at']
    ordering = ['-id']
    
    def get_queryset(self, request):
        """管理员可以看到所有绑定"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'house', 'approved_by')


@admin.register(PropertyFeeBill)
class PropertyFeeBillAdmin(admin.ModelAdmin):
    """物业费账单管理界面"""
    list_display = ['id', 'house_id', 'billing_period', 'amount', 'status', 'due_date', 'paid_at']
    search_fields = ['billing_period', 'house_id']
    list_filter = ['status', 'billing_period', 'due_date']
    ordering = ['-created_at']


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    """访客通行证管理界面"""
    list_display = ['id', 'visitor_name', 'visitor_phone', 'user_id', 'house_id', 'status', 'valid_from', 'valid_to']
    search_fields = ['visitor_name', 'visitor_phone', 'pass_code']
    list_filter = ['status', 'valid_from', 'valid_to']
    ordering = ['-created_at']
