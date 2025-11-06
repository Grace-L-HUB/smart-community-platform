from rest_framework import permissions
from apps.users.models import UserRole


class IsPropertyStaffOrAdmin(permissions.BasePermission):
    """
    物业人员或管理员权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 超级管理员总是有权限
        if request.user.is_superuser:
            return True
        
        # 检查是否是物业人员
        if hasattr(request.user, 'role_id') and request.user.role_id:
            try:
                role = UserRole.objects.get(id=request.user.role_id)
                return role.role_type == UserRole.RoleType.PROPERTY
            except UserRole.DoesNotExist:
                return False
        
        return False


class IsResidentOrAdmin(permissions.BasePermission):
    """
    居民或管理员权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 超级管理员总是有权限
        if request.user.is_superuser:
            return True
        
        # 检查是否是居民
        if hasattr(request.user, 'role_id') and request.user.role_id:
            try:
                role = UserRole.objects.get(id=request.user.role_id)
                return role.role_type == UserRole.RoleType.RESIDENT
            except UserRole.DoesNotExist:
                return False
        
        # 没有角色的用户默认为居民
        return True


class IsOwnerOrPropertyStaff(permissions.BasePermission):
    """
    资源所有者或物业人员权限
    """
    def has_object_permission(self, request, view, obj):
        # 超级管理员总是有权限
        if request.user.is_superuser:
            return True
        
        # 物业人员有权限
        if hasattr(request.user, 'role_id') and request.user.role_id:
            try:
                role = UserRole.objects.get(id=request.user.role_id)
                if role.role_type == UserRole.RoleType.PROPERTY:
                    return True
            except UserRole.DoesNotExist:
                pass
        
        # 检查是否是资源所有者
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id
        
        return False


class CommunityViewPermission(permissions.BasePermission):
    """
    社区管理权限控制
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 查看权限：所有认证用户
        if view.action in ['list', 'retrieve', 'buildings', 'houses']:
            return True
        
        # 创建、更新、删除权限：仅管理员和物业人员
        return request.user.is_superuser or self._is_property_staff(request.user)
    
    def _is_property_staff(self, user):
        """检查是否是物业人员"""
        if hasattr(user, 'role_id') and user.role_id:
            try:
                role = UserRole.objects.get(id=user.role_id)
                return role.role_type == UserRole.RoleType.PROPERTY
            except UserRole.DoesNotExist:
                return False
        return False


class UserHousePermission(permissions.BasePermission):
    """
    用户房产绑定权限控制
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 查看权限：所有认证用户可以查看
        if view.action in ['list', 'retrieve', 'my_houses']:
            return True
        
        # 申请权限：所有认证用户
        if view.action == 'apply':
            return True
        
        # 审批权限：仅管理员和物业人员
        if view.action in ['approve', 'pending_approvals']:
            return request.user.is_superuser or self._is_property_staff(request.user)
        
        # 其他操作权限：管理员和物业人员
        return request.user.is_superuser or self._is_property_staff(request.user)
    
    def has_object_permission(self, request, view, obj):
        # 超级管理员总是有权限
        if request.user.is_superuser:
            return True
        
        # 物业人员有权限
        if self._is_property_staff(request.user):
            return True
        
        # 用户只能操作自己的绑定
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return obj.user == request.user
        
        return False
    
    def _is_property_staff(self, user):
        """检查是否是物业人员"""
        if hasattr(user, 'role_id') and user.role_id:
            try:
                role = UserRole.objects.get(id=user.role_id)
                return role.role_type == UserRole.RoleType.PROPERTY
            except UserRole.DoesNotExist:
                return False
        return False


class PropertyBillPermission(permissions.BasePermission):
    """
    物业费账单权限控制
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 查看权限：所有认证用户
        if view.action in ['list', 'retrieve']:
            return True
        
        # 创建、更新、删除权限：仅管理员和物业人员
        return request.user.is_superuser or self._is_property_staff(request.user)
    
    def _is_property_staff(self, user):
        """检查是否是物业人员"""
        if hasattr(user, 'role_id') and user.role_id:
            try:
                role = UserRole.objects.get(id=user.role_id)
                return role.role_type == UserRole.RoleType.PROPERTY
            except UserRole.DoesNotExist:
                return False
        return False


class VisitorPassPermission(permissions.BasePermission):
    """
    访客通行证权限控制
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 所有认证用户都可以创建和查看通行证
        if view.action in ['list', 'retrieve', 'create']:
            return True
        
        # 取消和使用操作在对象级别权限中处理
        if view.action in ['cancel', 'use']:
            return True
        
        # 其他操作权限：管理员和物业人员
        return request.user.is_superuser or self._is_property_staff(request.user)
    
    def has_object_permission(self, request, view, obj):
        # 超级管理员总是有权限
        if request.user.is_superuser:
            return True
        
        # 物业人员有权限
        if self._is_property_staff(request.user):
            return True
        
        # 用户只能操作自己创建的通行证
        return obj.user_id == request.user.id
    
    def _is_property_staff(self, user):
        """检查是否是物业人员"""
        if hasattr(user, 'role_id') and user.role_id:
            try:
                role = UserRole.objects.get(id=user.role_id)
                return role.role_type == UserRole.RoleType.PROPERTY
            except UserRole.DoesNotExist:
                return False
        return False
