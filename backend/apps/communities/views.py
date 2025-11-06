from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from .models import Community, Building, House, UserHouse
from .serializers import (
    CommunitySerializer, CommunityDetailSerializer,
    BuildingSerializer, BuildingListSerializer,
    HouseSerializer, HouseListSerializer,
    UserHouseSerializer, UserHouseCreateSerializer, UserHouseApprovalSerializer
)


class CommunityViewSet(viewsets.ModelViewSet):
    """小区视图集"""
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + ([DjangoFilterBackend] if DjangoFilterBackend else [])
    filterset_fields = ['name'] if DjangoFilterBackend else None
    search_fields = ['name', 'address']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'retrieve':
            return CommunityDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """创建小区时设置创建者"""
        serializer.save()

    @action(detail=True, methods=['get'])
    def buildings(self, request, pk=None):
        """获取小区下的所有楼栋"""
        community = self.get_object()
        buildings = community.buildings.all()
        serializer = BuildingListSerializer(buildings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取小区统计信息"""
        community = self.get_object()
        buildings_count = community.buildings.count()
        houses_count = House.objects.filter(building__community=community).count()

        return Response({
            'buildings_count': buildings_count,
            'houses_count': houses_count,
        })


class BuildingViewSet(viewsets.ModelViewSet):
    """楼栋视图集"""
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + ([DjangoFilterBackend] if DjangoFilterBackend else [])
    filterset_fields = ['community'] if DjangoFilterBackend else None
    search_fields = ['name']
    ordering_fields = ['name', 'unit_count']
    ordering = ['name']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return BuildingListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """创建楼栋"""
        serializer.save()

    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """获取楼栋下的所有房屋"""
        building = self.get_object()
        houses = building.houses.all()
        serializer = HouseListSerializer(houses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取楼栋统计信息"""
        building = self.get_object()
        houses_count = building.houses.count()
        total_area = building.houses.aggregate(total_area=Sum('area'))['total_area'] or 0

        return Response({
            'houses_count': houses_count,
            'total_area': total_area,
        })


class HouseViewSet(viewsets.ModelViewSet):
    """房屋视图集"""
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + ([DjangoFilterBackend] if DjangoFilterBackend else [])
    filterset_fields = ['building', 'building__community'] if DjangoFilterBackend else None
    search_fields = ['number', 'owner_name']
    ordering_fields = ['number', 'area', 'owner_name']
    ordering = ['number']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return HouseListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """创建房屋"""
        serializer.save()

    @action(detail=True, methods=['get'])
    def user_houses(self, request, pk=None):
        """获取房屋的用户绑定信息"""
        house = self.get_object()
        user_houses = house.user_houses.all()
        serializer = UserHouseSerializer(user_houses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_houses(self, request):
        """获取当前用户的房产"""
        if not request.user.is_authenticated:
            return Response(
                {'error': '需要登录才能查看房产信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_houses = UserHouse.objects.filter(
            user=request.user,
            status=UserHouse.StatusType.APPROVED
        )
        serializer = UserHouseSerializer(user_houses, many=True)
        return Response(serializer.data)


class UserHouseViewSet(viewsets.ModelViewSet):
    """用户房产绑定视图集"""
    queryset = UserHouse.objects.all()
    serializer_class = UserHouseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter] if DjangoFilterBackend else [filters.OrderingFilter]
    filterset_fields = ['user', 'house', 'status', 'relationship'] if DjangoFilterBackend else None
    ordering_fields = ['approved_at']  # UserHouse doesn't have created_at
    ordering = ['-approved_at']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return UserHouseCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserHouseApprovalSerializer
        return self.serializer_class

    def get_queryset(self):
        """获取查询集"""
        queryset = UserHouse.objects.all()

        # 普通用户只能看到自己的绑定记录
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        """创建房产绑定申请"""
        import uuid
        # Generate a unique ID for the UserHouse
        user_house_id = abs(hash(str(uuid.uuid4()))) % (10**9)  # Generate a positive 9-digit ID
        serializer.save(id=user_house_id, user=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审核通过房产绑定"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {'error': '没有权限进行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_house = self.get_object()
        if user_house.status != UserHouse.StatusType.PENDING:
            return Response(
                {'error': '只能审核待审核的申请'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_house.status = UserHouse.StatusType.APPROVED
        user_house.approved_by = request.user
        user_house.save()

        serializer = UserHouseSerializer(user_house)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """审核拒绝房产绑定"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {'error': '没有权限进行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_house = self.get_object()
        if user_house.status != UserHouse.StatusType.PENDING:
            return Response(
                {'error': '只能审核待审核的申请'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_house.status = UserHouse.StatusType.REJECTED
        user_house.approved_by = request.user
        user_house.save()

        serializer = UserHouseSerializer(user_house)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """获取待审核的申请"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {'error': '没有权限进行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )

        pending_user_houses = UserHouse.objects.filter(
            status=UserHouse.StatusType.PENDING
        )
        serializer = UserHouseSerializer(pending_user_houses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """获取当前用户的申请"""
        user_houses = UserHouse.objects.filter(user=request.user)
        serializer = UserHouseSerializer(user_houses, many=True)
        return Response(serializer.data)

