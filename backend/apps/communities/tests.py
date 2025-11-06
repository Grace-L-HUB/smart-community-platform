from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Community, Building, House, UserHouse

User = get_user_model()


class CommunityModelTest(TestCase):
    """社区模型测试"""

    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )

    def test_community_str(self):
        """测试社区字符串表示"""
        self.assertEqual(str(self.community), "测试小区")

    def test_community_fee_standard_validation(self):
        """测试物业费标准验证"""
        # 测试负数
        with self.assertRaises(Exception):
            community = Community(
                name="错误小区",
                address="测试地址",
                property_phone="12345678901",
                fee_standard=Decimal("-1.00")
            )
            community.full_clean()  # 触发验证器
            community.save()


class BuildingModelTest(TestCase):
    """楼栋模型测试"""

    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )
        self.building = Building.objects.create(
            community=self.community,
            name="1栋",
            unit_count=2
        )

    def test_building_str(self):
        """测试楼栋字符串表示"""
        self.assertEqual(str(self.building), "测试小区-1栋")

    def test_building_unique_constraint(self):
        """测试楼栋唯一性约束"""
        with self.assertRaises(Exception):
            Building.objects.create(
                community=self.community,
                name="1栋",
                unit_count=1
            )


class HouseModelTest(TestCase):
    """房屋模型测试"""

    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )
        self.building = Building.objects.create(
            community=self.community,
            name="1栋",
            unit_count=2
        )
        self.house = House.objects.create(
            id=1,
            building=self.building,
            unit="1单元",
            number="101",
            area=Decimal("100.50"),
            owner_name="张三"
        )

    def test_house_str(self):
        """测试房屋字符串表示"""
        expected = "测试小区-1栋-1单元-101"
        self.assertEqual(str(self.house), expected)

    def test_house_unique_constraint(self):
        """测试房屋唯一性约束"""
        with self.assertRaises(Exception):
            House.objects.create(
                id=2,
                building=self.building,
                unit="1单元",
                number="101",
                area=Decimal("80.00")
            )


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
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )
        self.building = Building.objects.create(
            community=self.community,
            name="1栋",
            unit_count=2
        )
        self.house = House.objects.create(
            id=1,
            building=self.building,
            unit="1单元",
            number="101",
            area=Decimal("100.50"),
            owner_name="张三"
        )
        self.user_house = UserHouse.objects.create(
            id=1,
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )

    def test_user_house_str(self):
        """测试用户房产绑定字符串表示"""
        expected = f"{self.user.username} - {self.house}"
        self.assertEqual(str(self.user_house), expected)

    def test_user_house_unique_constraint(self):
        """测试用户房产绑定唯一性约束"""
        with self.assertRaises(Exception):
            UserHouse.objects.create(
                id=2,
                user=self.user,
                house=self.house,
                relationship=UserHouse.RelationshipType.FAMILY
            )


class CommunityAPITest(APITestCase):
    """社区API测试"""

    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )

    def test_get_communities_list(self):
        """测试获取社区列表"""
        url = reverse('community-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_community_detail(self):
        """测试获取社区详情"""
        url = reverse('community-detail', kwargs={'pk': self.community.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '测试小区')

    def test_create_community_unauthorized(self):
        """测试未授权创建社区"""
        url = reverse('community-list')
        data = {
            'name': '新小区',
            'address': '新地址',
            'property_phone': '12345678901',
            'fee_standard': '3.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_community_authorized(self):
        """测试授权创建社区"""
        self.client.force_authenticate(user=self.user)
        url = reverse('community-list')
        data = {
            'name': '新小区',
            'address': '新地址',
            'property_phone': '12345678901',
            'fee_standard': '3.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Community.objects.count(), 2)

    def test_community_buildings_action(self):
        """测试获取社区楼栋"""
        # 创建楼栋
        building = Building.objects.create(
            community=self.community,
            name="1栋",
            unit_count=2
        )

        url = reverse('community-buildings', kwargs={'pk': self.community.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class BuildingAPITest(APITestCase):
    """楼栋API测试"""

    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )
        self.building = Building.objects.create(
            community=self.community,
            name="1栋",
            unit_count=2
        )
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )

    def test_get_buildings_list(self):
        """测试获取楼栋列表"""
        url = reverse('building-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_building_detail(self):
        """测试获取楼栋详情"""
        url = reverse('building-detail', kwargs={'pk': self.building.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '1栋')

    def test_filter_buildings_by_community(self):
        """测试按小区筛选楼栋"""
        url = reverse('building-list')
        response = self.client.get(url, {'community': self.community.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class HouseAPITest(APITestCase):
    """房屋API测试"""

    def setUp(self):
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )
        self.building = Building.objects.create(
            community=self.community,
            name="1栋",
            unit_count=2
        )
        self.house = House.objects.create(
            id=1,
            building=self.building,
            unit="1单元",
            number="101",
            area=Decimal("100.50"),
            owner_name="张三"
        )
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )

    def test_get_houses_list(self):
        """测试获取房屋列表"""
        url = reverse('house-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_house_detail(self):
        """测试获取房屋详情"""
        url = reverse('house-detail', kwargs={'pk': self.house.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number'], '101')

    def test_my_houses_action_unauthorized(self):
        """测试未授权获取我的房产"""
        url = reverse('house-my-houses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_houses_action_authorized(self):
        """测试授权获取我的房产"""
        # 创建用户房产绑定
        UserHouse.objects.create(
            id=1,
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.APPROVED
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('house-my-houses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class UserHouseAPITest(APITestCase):
    """用户房产绑定API测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            phone="13800138000",
            password="testpass123"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            phone="13800138001",
            password="adminpass123",
            is_staff=True
        )
        self.community = Community.objects.create(
            name="测试小区",
            address="测试地址",
            property_phone="12345678901",
            fee_standard=Decimal("2.50")
        )
        self.building = Building.objects.create(
            community=self.community,
            name="1栋",
            unit_count=2
        )
        self.house = House.objects.create(
            id=1,
            building=self.building,
            unit="1单元",
            number="101",
            area=Decimal("100.50"),
            owner_name="张三"
        )

    def test_create_user_house_binding(self):
        """测试创建用户房产绑定"""
        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-list')
        data = {
            'house': self.house.pk,
            'relationship': UserHouse.RelationshipType.OWNER,
            'certificate_image': 'http://example.com/cert.jpg'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserHouse.objects.count(), 1)

    def test_create_user_house_binding_without_cert(self):
        """测试业主绑定但没有房产证"""
        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-list')
        data = {
            'house': self.house.pk,
            'relationship': UserHouse.RelationshipType.OWNER,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_my_applications(self):
        """测试获取我的申请"""
        # 创建绑定记录
        UserHouse.objects.create(
            id=1,
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-my-applications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_approve_user_house_as_admin(self):
        """测试管理员审核通过"""
        # 创建待审核的绑定记录
        user_house = UserHouse.objects.create(
            id=1,
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('userhouse-approve', kwargs={'pk': user_house.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 刷新对象
        user_house.refresh_from_db()
        self.assertEqual(user_house.status, UserHouse.StatusType.APPROVED)
        self.assertEqual(user_house.approved_by, self.admin_user)

    def test_approve_user_house_as_user(self):
        """测试普通用户审核通过（应该失败）"""
        user_house = UserHouse.objects.create(
            id=1,
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-approve', kwargs={'pk': user_house.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_approvals_as_admin(self):
        """测试管理员获取待审核申请"""
        UserHouse.objects.create(
            id=1,
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('userhouse-pending-approvals')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_pending_approvals_as_user(self):
        """测试普通用户获取待审核申请（应该失败）"""
        UserHouse.objects.create(
            id=1,
            user=self.user,
            house=self.house,
            relationship=UserHouse.RelationshipType.OWNER,
            status=UserHouse.StatusType.PENDING
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('userhouse-pending-approvals')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
