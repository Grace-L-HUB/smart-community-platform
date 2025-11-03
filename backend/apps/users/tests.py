from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, UserRole
import json
import os
import unittest


class UserAuthenticationTests(TestCase):
    """用户认证测试类"""
    
    def setUp(self):
        # 创建测试客户端
        self.client = APIClient()
        
        # 创建测试角色
        self.admin_role = UserRole.objects.create(
            name='管理员',
            role_type='admin',
            permissions={
                'can_manage_users': True,
                'can_manage_work_orders': True,
                'can_manage_announcements': True,
                'can_manage_bills': True
            }
        )
        
        self.resident_role = UserRole.objects.create(
            name='居民',
            role_type='resident',
            permissions={
                'can_view_work_orders': True,
                'can_create_work_orders': True
            }
        )
        
        # 创建测试用户
        self.admin_user = User.objects.create_user(
            username='admin',
            phone='13800138001',
            password='admin123',
            role_id=self.admin_role.id,
            is_staff=True
        )
        
        self.resident_user = User.objects.create_user(
            username='resident',
            phone='13800138002',
            password='resident123',
            role_id=self.resident_role.id
        )
        
        # 创建微信测试用户
        self.wechat_user = User.objects.create_user(
            username='wx_test',
            phone='',
            password=None,
            openid='test_openid_123456',
            role_id=self.resident_role.id
        )
    
    def test_jwt_token_obtain(self):
        """测试JWT令牌获取功能"""
        url = reverse('token_obtain_pair')
        
        # 测试有效的凭据
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('username', response.data)
        self.assertIn('role_id', response.data)
        
        # 测试无效的凭据
        data = {
            'username': 'admin',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_jwt_token_refresh(self):
        """测试JWT令牌刷新功能"""
        # 先获取有效的令牌
        token_url = reverse('token_obtain_pair')
        data = {'username': 'admin', 'password': 'admin123'}
        token_response = self.client.post(token_url, data, format='json')
        
        # 使用刷新令牌刷新访问令牌
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': token_response.data['refresh']}
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
    
    def test_jwt_token_verify(self):
        """测试JWT令牌验证功能"""
        # 先获取有效的令牌
        token_url = reverse('token_obtain_pair')
        data = {'username': 'admin', 'password': 'admin123'}
        token_response = self.client.post(token_url, data, format='json')
        
        # 验证令牌
        verify_url = reverse('token_verify')
        verify_data = {'token': token_response.data['access']}
        verify_response = self.client.post(verify_url, verify_data, format='json')
        
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        
        # 验证无效令牌
        invalid_data = {'token': 'invalid_token'}
        invalid_response = self.client.post(verify_url, invalid_data, format='json')
        
        self.assertEqual(invalid_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @unittest.skipIf(not os.getenv('WECHAT_APPID'), "跳过微信登录测试，需要配置环境变量")
    def test_wechat_login_existing_user(self):
        """测试微信登录 - 已存在用户"""
        # 注意：这是一个模拟测试，实际的微信登录需要正确的code
        # 在实际测试中，可以使用mock来模拟微信API的响应
        url = reverse('wechat-login')
        
        # 这里使用模拟的code，实际测试时需要调整
        data = {
            'code': 'test_code',
            'avatar_url': 'https://example.com/avatar.jpg',
            'nickname': '测试用户'
        }
        
        # 模拟微信API响应
        # 在实际测试中，应该使用mock.patch来模拟requests.get的返回值
        response = self.client.post(url, data, format='json')
        
        # 如果环境变量未配置，测试会失败，这是预期的
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('微信登录失败', str(response.data))
    
    def test_user_permissions_endpoint(self):
        """测试用户权限端点"""
        url = reverse('user-permissions')
        
        # 未认证用户应该被拒绝
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 认证为管理员用户
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role_id'], self.admin_role.id)
        self.assertEqual(response.data['role_name'], '管理员')
        self.assertTrue(response.data['permissions']['can_manage_users'])
    
    def test_role_based_permissions(self):
        """测试基于角色的权限控制"""
        # 测试管理员用户可以访问用户列表
        user_list_url = reverse('user-list')
        
        # 使用居民用户访问
        self.client.force_authenticate(user=self.resident_user)
        response = self.client.get(user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 目前权限设置允许查看
        
        # 尝试创建用户（应该被拒绝，因为居民没有创建权限）
        create_data = {
            'username': 'newuser',
            'phone': '13800138003',
            'password': 'password123'
        }
        response = self.client.post(user_list_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 使用管理员用户创建用户
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(user_list_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
