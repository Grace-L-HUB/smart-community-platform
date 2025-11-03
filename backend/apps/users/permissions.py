from rest_framework import permissions
from .models import UserRole


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可以进行所有操作，普通用户只读"""
    
    def has_permission(self, request, view):
        # 允许所有用户的GET、HEAD、OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        # 其他请求需要管理员权限
        return request.user.is_authenticated and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """对象所有者可以修改，其他用户只读"""
    
    def has_object_permission(self, request, view, obj):
        # 允许所有用户的GET、HEAD、OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        # 其他请求需要是对象所有者
        return obj.id == request.user.id


class RoleBasedPermission(permissions.BasePermission):
    """基于角色的权限控制"""
    required_permission = None
    required_role_type = None
    
    def has_permission(self, request, view):
        # 未认证用户没有权限
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 检查是否有角色
        if not request.user.role_id:
            return False
        
        try:
            # 获取用户角色
            role = UserRole.objects.get(id=request.user.role_id)
            
            # 检查角色类型
            if self.required_role_type and role.role_type != self.required_role_type:
                return False
            
            # 检查特定权限
            if self.required_permission:
                return role.permissions.get(self.required_permission, False)
            
            return True
        except UserRole.DoesNotExist:
            return False


class IsCommunityManager(RoleBasedPermission):
    """社区管理员权限"""
    required_role_type = 'community_manager'


class IsPropertyManager(RoleBasedPermission):
    """物业管理员权限"""
    required_role_type = 'property_manager'


class IsResident(RoleBasedPermission):
    """居民权限"""
    required_role_type = 'resident'


class HasWorkOrderPermission(RoleBasedPermission):
    """工单相关权限"""
    required_permission = 'can_manage_work_orders'


class HasAnnouncementPermission(RoleBasedPermission):
    """公告相关权限"""
    required_permission = 'can_manage_announcements'


class HasBillPermission(RoleBasedPermission):
    """账单相关权限"""
    required_permission = 'can_manage_bills'