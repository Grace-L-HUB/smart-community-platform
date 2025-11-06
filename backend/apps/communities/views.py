from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils import timezone

from .models import Community, Building, House, UserHouse, PropertyFeeBill, VisitorPass
from .serializers import (
    CommunitySerializer, BuildingSerializer, BuildingDetailSerializer,
    HouseSerializer, HouseDetailSerializer, UserHouseSerializer,
    UserHouseApplicationSerializer, UserHouseApprovalSerializer,
    PropertyFeeBillSerializer, VisitorPassSerializer
)
from .permissions import (
    CommunityViewPermission, UserHousePermission, PropertyBillPermission,
    VisitorPassPermission
)


class CommunityViewSet(viewsets.ModelViewSet):
    """小区管理ViewSet"""
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [CommunityViewPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def buildings(self, request, pk=None):
        """获取小区下的所有楼栋"""
        community = self.get_object()
        buildings = community.buildings.all()
        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """获取小区下的所有房屋"""
        community = self.get_object()
        houses = House.objects.filter(building__community=community)
        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)


class BuildingViewSet(viewsets.ModelViewSet):
    """楼栋管理ViewSet"""
    queryset = Building.objects.all()
    permission_classes = [CommunityViewPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['community']
    search_fields = ['name', 'community__name']
    ordering_fields = ['name']
    ordering = ['community', 'name']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action in ['retrieve', 'list']:
            return BuildingDetailSerializer
        return BuildingSerializer
    
    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """获取楼栋下的所有房屋"""
        building = self.get_object()
        houses = building.houses.all()
        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)


class HouseViewSet(viewsets.ModelViewSet):
    """房屋管理ViewSet"""
    queryset = House.objects.all()
    permission_classes = [CommunityViewPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['building', 'building__community']
    search_fields = ['unit', 'number', 'owner_name', 'building__name', 'building__community__name']
    ordering_fields = ['unit', 'number']
    ordering = ['building', 'unit', 'number']
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action in ['retrieve', 'list']:
            return HouseDetailSerializer
        return HouseSerializer
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """获取房屋绑定的用户"""
        house = self.get_object()
        user_houses = house.user_houses.filter(status=UserHouse.StatusType.APPROVED)
        serializer = UserHouseSerializer(user_houses, many=True)
        return Response(serializer.data)


class UserHouseViewSet(viewsets.ModelViewSet):
    """用户房产绑定管理ViewSet"""
    queryset = UserHouse.objects.all()
    serializer_class = UserHouseSerializer
    permission_classes = [UserHousePermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'relationship', 'user', 'house']
    search_fields = ['user__username', 'user__phone', 'house__unit', 'house__number']
    ordering = ['-id']
    
    def get_queryset(self):
        """根据用户角色过滤数据"""
        user = self.request.user
        if user.is_superuser:
            # 超级管理员可以看到所有绑定
            return UserHouse.objects.all()
        elif hasattr(user, 'role_id') and user.role_id:
            # 物业人员可以看到所有绑定用于审核
            return UserHouse.objects.all()
        else:
            # 普通用户只能看到自己的绑定
            return UserHouse.objects.filter(user=user)
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'apply':
            return UserHouseApplicationSerializer
        elif self.action == 'approve':
            return UserHouseApprovalSerializer
        return UserHouseSerializer
    
    @action(detail=False, methods=['post'])
    def apply(self, request):
        """用户申请房产绑定"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_house = serializer.save()
            return Response(
                UserHouseSerializer(user_house).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """审批房产绑定申请（仅限管理员和物业人员）"""
        if not (request.user.is_superuser or (hasattr(request.user, 'role_id') and request.user.role_id)):
            return Response(
                {'detail': '无权限进行审批操作'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_house = self.get_object()
        serializer = self.get_serializer(user_house, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(UserHouseSerializer(user_house).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_houses(self, request):
        """获取当前用户的房产绑定"""
        user_houses = UserHouse.objects.filter(
            user=request.user,
            status=UserHouse.StatusType.APPROVED
        )
        serializer = UserHouseSerializer(user_houses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """获取待审批的房产绑定（仅限管理员和物业人员）"""
        if not (request.user.is_superuser or (hasattr(request.user, 'role_id') and request.user.role_id)):
            return Response(
                {'detail': '无权限查看审批列表'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_houses = UserHouse.objects.filter(status=UserHouse.StatusType.PENDING)
        serializer = UserHouseSerializer(pending_houses, many=True)
        return Response(serializer.data)


class PropertyFeeBillViewSet(viewsets.ModelViewSet):
    """物业费账单管理ViewSet"""
    queryset = PropertyFeeBill.objects.all()
    serializer_class = PropertyFeeBillSerializer
    permission_classes = [PropertyBillPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'billing_period']
    search_fields = ['billing_period']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户角色过滤数据"""
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'role_id') and user.role_id):
            # 管理员和物业人员可以看到所有账单
            return PropertyFeeBill.objects.all()
        else:
            # 普通用户只能看到自己房屋的账单
            user_house_ids = UserHouse.objects.filter(
                user=user, 
                status=UserHouse.StatusType.APPROVED
            ).values_list('house_id', flat=True)
            return PropertyFeeBill.objects.filter(house_id__in=user_house_ids)
    


class VisitorPassViewSet(viewsets.ModelViewSet):
    """访客通行证管理ViewSet"""
    queryset = VisitorPass.objects.all()
    serializer_class = VisitorPassSerializer
    permission_classes = [VisitorPassPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'user_id', 'house_id']
    search_fields = ['visitor_name', 'visitor_phone']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户角色过滤数据"""
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'role_id') and user.role_id):
            # 管理员和物业人员可以看到所有通行证
            return VisitorPass.objects.all()
        else:
            # 普通用户只能看到自己创建的通行证
            return VisitorPass.objects.filter(user_id=user.id)
    
    def perform_create(self, serializer):
        """创建时自动设置用户ID和通行码"""
        import uuid
        serializer.save(
            user_id=self.request.user.id,
            pass_code=str(uuid.uuid4())[:16]  # 生成16位通行码
        )
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """取消通行证"""
        visitor_pass = self.get_object()
        
        # 只有创建者或管理员可以取消
        if visitor_pass.user_id != request.user.id and not request.user.is_superuser:
            return Response(
                {'detail': '无权限取消此通行证'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        visitor_pass.status = VisitorPass.PassStatus.CANCELLED
        visitor_pass.save()
        
        serializer = VisitorPassSerializer(visitor_pass)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def use(self, request, pk=None):
        """使用通行证（标记为已使用）"""
        visitor_pass = self.get_object()
        
        # 检查通行证状态和有效期
        if visitor_pass.status != VisitorPass.PassStatus.ACTIVE:
            return Response(
                {'detail': '通行证状态不正确'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        now = timezone.now()
        if now < visitor_pass.valid_from or now > visitor_pass.valid_to:
            return Response(
                {'detail': '通行证已过期或未到有效期'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        visitor_pass.status = VisitorPass.PassStatus.USED
        visitor_pass.save()
        
        serializer = VisitorPassSerializer(visitor_pass)
        return Response(serializer.data)
