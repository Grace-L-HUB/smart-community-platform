from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

from .models import Community, Building, House, UserHouse, PropertyFeeBill, VisitorPass
from apps.users.models import UserRole


User = get_user_model()


class CommunityModelTest(TestCase):
    """小区模型测试"""
    
    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址123号",
            property_phone="400-123-4567",
            fee_standard=Decimal('2.50')
        )
    
    def test_community_creation(self):
        """测试小区创建"""
        self.assertEqual(self.community.name, "测试小区")
        self.assertEqual(self.community.address, "测试地址123号")
        self.assertEqual(self.community.property_phone, "400-123-4567")
        self.assertEqual(self.community.fee_standard, Decimal('2.50'))
    
    def test_community_str(self):
        """测试小区字符串表示"""
        self.assertEqual(str(self.community), "测试小区")


class BuildingModelTest(TestCase):
    """楼栋模型测试"""
    
    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址123号",
            property_phone="400-123-4567",
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name="A栋",
            unit_count=3
        )
    
    def test_building_creation(self):
        """测试楼栋创建"""
        self.assertEqual(self.building.community, self.community)
        self.assertEqual(self.building.name, "A栋")
        self.assertEqual(self.building.unit_count, 3)
    
    def test_building_str(self):
        """测试楼栋字符串表示"""
        self.assertEqual(str(self.building), "测试小区-A栋")


class HouseModelTest(TestCase):
    """房屋模型测试"""
    
    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址123号",
            property_phone="400-123-4567",
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name="A栋",
            unit_count=3
        )
        self.house = House.objects.create(
            id=1001,
            building=self.building,
            unit="1",
            number="101",
            area=Decimal('89.5'),
            owner_name="张三"
        )
    
    def test_house_creation(self):
        """测试房屋创建"""
        self.assertEqual(self.house.building, self.building)
        self.assertEqual(self.house.unit, "1")
        self.assertEqual(self.house.number, "101")
        self.assertEqual(self.house.area, Decimal('89.5'))
        self.assertEqual(self.house.owner_name, "张三")
    
    def test_house_str(self):
        """测试房屋字符串表示"""
        self.assertEqual(str(self.house), "测试小区-A栋-1-101")


class UserHouseModelTest(TestCase):
    """用户房产绑定模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址123号",
            property_phone="400-123-4567",
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name="A栋",
            unit_count=3
        )
        self.house = House.objects.create(
            id=1001,
            building=self.building,
            unit="1",
            number="101",
            area=Decimal('89.5'),
            owner_name="张三"
        )
        self.user_house = UserHouse.objects.create(
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )
    
    def test_user_house_creation(self):
        """测试用户房产绑定创建"""
        self.assertEqual(self.user_house.user, self.user)
        self.assertEqual(self.user_house.house, self.house)
        self.assertEqual(self.user_house.relationship, UserHouse.RelationshipType.OWNER)
        self.assertEqual(self.user_house.status, UserHouse.StatusType.PENDING)
    
    def test_user_house_str(self):
        """测试用户房产绑定字符串表示"""
        self.assertEqual(str(self.user_house), "testuser - 测试小区-A栋-1-101")


class CommunityAPITest(APITestCase):
    """小区API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            phone="13800138001",
            password="adminpass123"
        )
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址123号",
            property_phone="400-123-4567",
            fee_standard=Decimal('2.50')
        )
        self.client = APIClient()
    
    def test_community_list_authenticated(self):
        """测试认证用户可以获取小区列表"""
        self.client.force_authenticate(user=self.user)
        url = reverse('community-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_community_list_unauthenticated(self):
        """测试未认证用户无法获取小区列表"""
        url = reverse('community-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_community_create_admin(self):
        """测试管理员可以创建小区"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('community-list')
        data = {
            'name': '新测试小区',
            'address': '新测试地址456号',
            'property_phone': '400-987-6543',
            'fee_standard': '3.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Community.objects.count(), 2)
    
    def test_community_create_regular_user(self):
        """测试普通用户无法创建小区"""
        self.client.force_authenticate(user=self.user)
        url = reverse('community-list')
        data = {
            'name': '新测试小区',
            'address': '新测试地址456号',
            'property_phone': '400-987-6543',
            'fee_standard': '3.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserHouseAPITest(APITestCase):
    """用户房产绑定API测试"""
    
    def setUp(self):
        # 创建用户
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            phone="13800138001",
            password="adminpass123"
        )
        
        # 创建物业角色和物业用户
        self.property_role = UserRole.objects.create(
            id=1,
            name="物业管理员",
            role_type=UserRole.RoleType.PROPERTY
        )
        self.property_user = User.objects.create_user(
            username="property",
            phone="13800138002",
            password="propertypass123",
            role_id=1
        )
        
        # 创建社区、楼栋、房屋
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址123号",
            property_phone="400-123-4567",
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name="A栋",
            unit_count=3
        )
        self.house = House.objects.create(
            id=1001,
            building=self.building,
            unit="1",
            number="101",
            area=Decimal('89.5'),
            owner_name="张三"
        )
        
        self.client = APIClient()
    
    def test_user_house_apply(self):
        """测试用户申请房产绑定"""
        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-apply')
        data = {
            'house': self.house.id,
            'relationship': UserHouse.RelationshipType.OWNER,
            'certificate_image': 'http://example.com/cert.jpg'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserHouse.objects.count(), 1)
        user_house = UserHouse.objects.first()
        self.assertEqual(user_house.status, UserHouse.StatusType.PENDING)
    
    def test_user_house_apply_duplicate(self):
        """测试用户重复申请同一房产"""
        # 先创建一个绑定
        UserHouse.objects.create(
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-apply')
        data = {
            'house': self.house.id,
            'relationship': UserHouse.RelationshipType.OWNER
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_house_approve_by_property(self):
        """测试物业人员审批房产绑定"""
        # 创建待审核的绑定
        user_house = UserHouse.objects.create(
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )
        
        self.client.force_authenticate(user=self.property_user)
        url = reverse('userhouse-approve', kwargs={'pk': user_house.id})
        data = {'status': UserHouse.StatusType.APPROVED}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user_house.refresh_from_db()
        self.assertEqual(user_house.status, UserHouse.StatusType.APPROVED)
        self.assertEqual(user_house.approved_by, self.property_user)
    
    def test_user_house_approve_by_regular_user(self):
        """测试普通用户无法审批房产绑定"""
        user_house = UserHouse.objects.create(
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-approve', kwargs={'pk': user_house.id})
        data = {'status': UserHouse.StatusType.APPROVED}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_my_houses(self):
        """测试获取用户已审核通过的房产"""
        UserHouse.objects.create(
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.APPROVED
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-my-houses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_pending_approvals_by_property(self):
        """测试物业人员获取待审批列表"""
        UserHouse.objects.create(
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )
        
        self.client.force_authenticate(user=self.property_user)
        url = reverse('userhouse-pending-approvals')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_pending_approvals_by_regular_user(self):
        """测试普通用户无法获取待审批列表"""
        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-pending-approvals')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VisitorPassAPITest(APITestCase):
    """访客通行证API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址123号",
            property_phone="400-123-4567",
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name="A栋",
            unit_count=3
        )
        self.house = House.objects.create(
            id=1001,
            building=self.building,
            unit="1",
            number="101",
            area=Decimal('89.5'),
            owner_name="张三"
        )
        self.client = APIClient()
    
    def test_visitor_pass_creation(self):
        """测试创建访客通行证"""
        self.client.force_authenticate(user=self.user)
        url = reverse('visitorpass-list')
        data = {
            'house_id': self.house.id,
            'visitor_name': '李四',
            'visitor_phone': '13900139000',
            'valid_from': '2024-12-01T10:00:00Z',
            'valid_to': '2024-12-01T18:00:00Z'
        }
        response = self.client.post(url, data)
        # 如果失败，打印错误信息以便调试
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VisitorPass.objects.count(), 1)
        
        visitor_pass = VisitorPass.objects.first()
        self.assertEqual(visitor_pass.user_id, self.user.id)
        self.assertEqual(visitor_pass.visitor_name, '李四')
    
    def test_visitor_pass_cancel(self):
        """测试取消访客通行证"""
        visitor_pass = VisitorPass.objects.create(
            user_id=self.user.id,
            house_id=self.house.id,
            visitor_name='李四',
            visitor_phone='13900139000',
            valid_from='2023-12-01T10:00:00Z',
            valid_to='2023-12-01T18:00:00Z',
            status=VisitorPass.PassStatus.ACTIVE
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('visitorpass-cancel', kwargs={'pk': visitor_pass.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        visitor_pass.refresh_from_db()
        self.assertEqual(visitor_pass.status, VisitorPass.PassStatus.CANCELLED)
