from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from apps.communities.models import Community, Building, House
from .models import Complaint

User = get_user_model()


class ComplaintModelTest(TestCase):
    """投诉模型测试"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='13800138000',
            password='testpass123'
        )
        self.community = Community.objects.create(
            name='测试社区',
            address='测试地址',
            property_phone='12345678901',
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name='1栋',
            unit_count=2
        )
        self.house = House.objects.create(
            id=1,
            building=self.building,
            unit='1单元',
            number='101',
            area=Decimal('100.50'),
            owner_name='测试用户'
        )

    def test_complaint_creation(self):
        """测试投诉创建"""
        complaint = Complaint.objects.create(
            id=1,
            user_id=self.user.id,
            house_id=self.house.id,
            type='噪音扰民',
            title='楼上噪音太大了',
            content='每天晚上都很吵，影响休息'
        )
        self.assertEqual(complaint.user_id, self.user.id)
        self.assertEqual(complaint.house_id, self.house.id)
        self.assertEqual(complaint.status, 'submitted')
        self.assertEqual(str(complaint), '投诉 #1 - 楼上噪音太大了')


class ComplaintSerializerTest(APITestCase):
    """投诉序列化器测试"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='13800138000',
            password='testpass123'
        )
        self.community = Community.objects.create(
            name='测试社区',
            address='测试地址',
            property_phone='12345678901',
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name='1栋',
            unit_count=2
        )
        self.house = House.objects.create(
            id=1,
            building=self.building,
            unit='1单元',
            number='101',
            area=Decimal('100.50'),
            owner_name='测试用户'
        )
        self.client.force_authenticate(user=self.user)

    def test_complaint_create_serializer_valid_data(self):
        """测试投诉创建序列化器有效数据"""
        data = {
            'house_id': self.house.id,
            'type': '噪音扰民',
            'title': '测试投诉标题',
            'content': '这是一个测试投诉内容，长度足够',
            'image_urls': ['http://example.com/image1.jpg', 'http://example.com/image2.jpg']
        }
        serializer = self.get_serializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_complaint_create_serializer_invalid_title(self):
        """测试投诉创建序列化器标题太短"""
        data = {
            'house_id': self.house.id,
            'type': '噪音扰民',
            'title': '太短',
            'content': '这是一个测试投诉内容，长度足够'
        }
        serializer = self.get_serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_complaint_create_serializer_invalid_content(self):
        """测试投诉创建序列化器内容太短"""
        data = {
            'house_id': self.house.id,
            'type': '噪音扰民',
            'title': '测试投诉标题',
            'content': '太短'
        }
        serializer = self.get_serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_complaint_create_serializer_too_many_images(self):
        """测试投诉创建序列化器图片太多"""
        data = {
            'house_id': self.house.id,
            'type': '噪音扰民',
            'title': '测试投诉标题',
            'content': '这是一个测试投诉内容，长度足够',
            'image_urls': [f'http://example.com/image{i}.jpg' for i in range(10)]
        }
        serializer = self.get_serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('image_urls', serializer.errors)

    def get_serializer(self, data=None):
        """获取序列化器"""
        from .serializers import ComplaintCreateSerializer
        return ComplaintCreateSerializer(data=data, context={'request': type('Request', (), {'user': self.user})()})


class ComplaintViewSetTest(APITestCase):
    """投诉视图集测试"""

    def setUp(self):
        """设置测试数据"""
        # 创建角色
        from apps.users.models import UserRole
        resident_role = UserRole.objects.create(
            id=1,
            name='居民',
            role_type='resident'
        )
        property_role = UserRole.objects.create(
            id=2,
            name='物业',
            role_type='property'
        )

        # 创建用户
        self.resident = User.objects.create_user(
            username='resident',
            phone='13800138001',
            password='testpass123',
            role_id=resident_role.id
        )
        self.property_staff = User.objects.create_user(
            username='property',
            phone='13800138002',
            password='testpass123',
            role_id=property_role.id,
            is_staff=True
        )

        # 创建社区和房产
        self.community = Community.objects.create(
            name='测试社区',
            address='测试地址',
            property_phone='12345678901',
            fee_standard=Decimal('2.50')
        )
        self.building = Building.objects.create(
            community=self.community,
            name='1栋',
            unit_count=2
        )
        self.house = House.objects.create(
            id=1,
            building=self.building,
            unit='1单元',
            number='101',
            area=Decimal('100.50'),
            owner_name='测试用户'
        )

        # 创建投诉
        self.complaint = Complaint.objects.create(
            id=1,
            user_id=self.resident.id,
            house_id=self.house.id,
            type='噪音扰民',
            title='测试投诉',
            content='这是一个测试投诉'
        )

    def test_resident_can_create_complaint(self):
        """测试居民可以创建投诉"""
        self.client.force_authenticate(user=self.resident)
        data = {
            'house_id': self.house.id,
            'type': '环境卫生',
            'title': '垃圾未及时清理',
            'content': '楼下垃圾已经好几天没有清理了'
        }
        response = self.client.post('/api/work-orders/complaints/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], '投诉提交成功')

    def test_property_staff_cannot_create_complaint(self):
        """测试物业人员不能创建投诉"""
        self.client.force_authenticate(user=self.property_staff)
        data = {
            'house_id': self.house.id,
            'type': '环境卫生',
            'title': '垃圾未及时清理',
            'content': '楼下垃圾已经好几天没有清理了'
        }
        response = self.client.post('/api/work-orders/complaints/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_can_view_own_complaints(self):
        """测试居民只能查看自己的投诉"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/work-orders/complaints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.complaint.id)

    def test_resident_cannot_view_others_complaints(self):
        """测试居民不能查看他人投诉"""
        other_user = User.objects.create_user(
            username='other',
            phone='13800138003',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get('/api/work-orders/complaints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_property_staff_can_view_all_complaints(self):
        """测试物业人员可以查看所有投诉"""
        self.client.force_authenticate(user=self.property_staff)
        response = self.client.get('/api/work-orders/complaints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_property_staff_can_process_complaint(self):
        """测试物业人员可以处理投诉"""
        self.client.force_authenticate(user=self.property_staff)
        data = {
            'status': 'processing',
            'process_remark': '我们已经安排人员处理'
        }
        response = self.client.patch(f'/api/work-orders/complaints/{self.complaint.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # 验证投诉状态已更新
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, 'processing')
        self.assertEqual(self.complaint.process_remark, '我们已经安排人员处理')

    def test_resident_cannot_process_complaint(self):
        """测试居民不能处理投诉"""
        self.client.force_authenticate(user=self.resident)
        data = {
            'status': 'processing',
            'process_remark': '请不要处理'
        }
        response = self.client.patch(f'/api/work-orders/complaints/{self.complaint.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_can_delete_own_unsubmitted_complaint(self):
        """测试居民可以删除自己的未处理投诉"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.delete(f'/api/work-orders/complaints/{self.complaint.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # 验证投诉已被删除
        with self.assertRaises(Complaint.DoesNotExist):
            Complaint.objects.get(id=self.complaint.id)

    def test_resident_cannot_delete_processed_complaint(self):
        """测试居民不能删除已处理的投诉"""
        # 先处理投诉
        self.complaint.status = 'resolved'
        self.complaint.save()

        self.client.force_authenticate(user=self.resident)
        response = self.client.delete(f'/api/work-orders/complaints/{self.complaint.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complaint_statistics_resident(self):
        """测试居民端投诉统计"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/work-orders/complaints/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertEqual(response.data['total'], 1)

    def test_complaint_statistics_property(self):
        """测试物业端投诉统计"""
        self.client.force_authenticate(user=self.property_staff)
        response = self.client.get('/api/work-orders/complaints/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('pending_over_3_days', response.data)

    def test_complaint_types_endpoint(self):
        """测试投诉类型接口"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/work-orders/complaints/complaint_types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) > 0)

    def test_complaint_supplement_resident(self):
        """测试居民可以补充投诉说明"""
        self.client.force_authenticate(user=self.resident)
        data = {
            'content': '这是补充的说明内容'
        }
        response = self.client.post(f'/api/work-orders/complaints/{self.complaint.id}/supplement/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # 验证内容已补充
        self.complaint.refresh_from_db()
        self.assertIn('补充的说明内容', self.complaint.content)

    def test_complaint_supplement_property_staff(self):
        """测试物业人员不能补充投诉说明"""
        self.client.force_authenticate(user=self.property_staff)
        data = {
            'content': '这是补充的说明内容'
        }
        response = self.client.post(f'/api/work-orders/complaints/{self.complaint.id}/supplement/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
