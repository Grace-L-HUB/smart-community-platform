from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None

from .models import Complaint
from .serializers import (
    ComplaintCreateSerializer,
    ComplaintListSerializer,
    ComplaintDetailSerializer,
    ComplaintProcessSerializer,
    ComplaintManageListSerializer,
    ComplaintManageDetailSerializer
)


class ComplaintViewSet(viewsets.ModelViewSet):
    """投诉建议视图集"""
    queryset = Complaint.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + ([DjangoFilterBackend] if DjangoFilterBackend else [])
    filterset_fields = ['status', 'type'] if DjangoFilterBackend else None
    search_fields = ['title', 'content', 'type']
    ordering_fields = ['submitted_at', 'processed_at']
    ordering = ['-submitted_at']

    def get_serializer_class(self):
        """根据不同的action返回不同的序列化器"""
        if self.action == 'create':
            return ComplaintCreateSerializer
        elif self.action == 'list':
            # 根据用户角色返回不同的序列化器
            if self.request.user.is_staff or self.request.user.is_superuser:
                return ComplaintManageListSerializer
            else:
                return ComplaintListSerializer
        elif self.action == 'retrieve':
            if self.request.user.is_staff or self.request.user.is_superuser:
                return ComplaintManageDetailSerializer
            else:
                return ComplaintDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return ComplaintProcessSerializer
        return ComplaintListSerializer

    def get_queryset(self):
        """根据用户角色过滤查询集"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # 物业人员可以查看所有投诉
            return Complaint.objects.all()
        else:
            # 居民只能查看自己的投诉
            return Complaint.objects.filter(user_id=user.id)

    def perform_create(self, serializer):
        """创建投诉时自动设置用户ID"""
        serializer.save(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """居民端提交投诉"""
        if request.user.is_staff or request.user.is_superuser:
            return Response(
                {"detail": _("物业人员不能提交投诉")},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "message": _("投诉提交成功"),
                "data": ComplaintDetailSerializer(
                    serializer.instance,
                    context={'request': request}
                ).data
            },
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """获取投诉详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """更新投诉（仅物业人员可以处理）"""
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": _("只有物业人员可以处理投诉")},
                status=status.HTTP_403_FORBIDDEN
            )

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": _("投诉处理成功"),
            "data": ComplaintManageDetailSerializer(
                instance,
                context={'request': request}
            ).data
        })

    def destroy(self, request, *args, **kwargs):
        """删除投诉（仅居民可以删除自己的未处理投诉）"""
        instance = self.get_object()

        # 只有居民可以删除投诉
        if request.user.is_staff or request.user.is_superuser:
            return Response(
                {"detail": _("物业人员不能删除投诉")},
                status=status.HTTP_403_FORBIDDEN
            )

        # 只能删除自己的投诉
        if instance.user_id != request.user.id:
            return Response(
                {"detail": _("只能删除自己的投诉")},
                status=status.HTTP_403_FORBIDDEN
            )

        # 只能删除未处理的投诉
        if instance.status != 'submitted':
            return Response(
                {"detail": _("只能删除未处理的投诉")},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(
            {"message": _("投诉删除成功")},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """投诉统计信息"""
        user = request.user

        if user.is_staff or user.is_superuser:
            # 物业端统计
            queryset = Complaint.objects.all()
            total = queryset.count()
            submitted = queryset.filter(status='submitted').count()
            processing = queryset.filter(status='processing').count()
            resolved = queryset.filter(status='resolved').count()
            rejected = queryset.filter(status='rejected').count()

            # 计算待处理天数统计
            pending_complaints = queryset.filter(status='submitted')
            pending_over_3_days = 0
            for complaint in pending_complaints:
                days = (timezone.now().date() - complaint.submitted_at.date()).days
                if days > 3:
                    pending_over_3_days += 1

            data = {
                "total": total,
                "submitted": submitted,
                "processing": processing,
                "resolved": resolved,
                "rejected": rejected,
                "pending_over_3_days": pending_over_3_days
            }
        else:
            # 居民端统计
            queryset = Complaint.objects.filter(user_id=user.id)
            total = queryset.count()
            submitted = queryset.filter(status='submitted').count()
            processing = queryset.filter(status='processing').count()
            resolved = queryset.filter(status='resolved').count()
            rejected = queryset.filter(status='rejected').count()

            data = {
                "total": total,
                "submitted": submitted,
                "processing": processing,
                "resolved": resolved,
                "rejected": rejected
            }

        return Response(data)

    @action(detail=True, methods=['post'])
    def supplement(self, request, pk=None):
        """居民端补充投诉说明"""
        if request.user.is_staff or request.user.is_superuser:
            return Response(
                {"detail": _("物业人员不能补充投诉说明")},
                status=status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()

        # 只能补充自己的投诉
        if instance.user_id != request.user.id:
            return Response(
                {"detail": _("只能补充自己的投诉说明")},
                status=status.HTTP_403_FORBIDDEN
            )

        # 只能补充未完成处理的投诉
        if instance.status not in ['submitted', 'processing']:
            return Response(
                {"detail": _("只能补充未完成处理的投诉说明")},
                status=status.HTTP_400_BAD_REQUEST
            )

        supplement_content = request.data.get('content', '').strip()
        if len(supplement_content) < 5:
            return Response(
                {"detail": _("补充说明至少需要5个字符")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 将补充说明添加到原有内容中
        instance.content += f"\n\n[补充说明 {timezone.now().strftime('%Y-%m-%d %H:%M')}]:\n{supplement_content}"
        instance.save()

        return Response({
            "message": _("补充说明添加成功"),
            "data": ComplaintDetailSerializer(
                instance,
                context={'request': request}
            ).data
        })

    @action(detail=False, methods=['get'])
    def complaint_types(self, request):
        """获取投诉类型列表"""
        types = [
            {"value": "噪音扰民", "label": "噪音扰民"},
            {"value": "环境卫生", "label": "环境卫生"},
            {"value": "公共设施", "label": "公共设施"},
            {"value": "安全隐患", "label": "安全隐患"},
            {"value": "物业服务", "label": "物业服务"},
            {"value": "邻里纠纷", "label": "邻里纠纷"},
            {"value": "违规停车", "label": "违规停车"},
            {"value": "其他问题", "label": "其他问题"},
        ]
        return Response(types)
