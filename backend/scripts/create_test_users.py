# 在backend目录下创建utils文件夹和脚本
import os
import sys
# 添加项目根目录到Python路径，使Django能找到config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django设置模块环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.users.models import User, UserRole

def create_test_users():
    # 创建角色，注意使用正确的role_type值和设置明确的id
    admin_role, _ = UserRole.objects.get_or_create(
        id=1,
        name='管理员',
        defaults={'role_type': 'property', 'permissions': {'can_manage_users': True}}
    )
    
    resident_role, _ = UserRole.objects.get_or_create(
        id=2,
        name='居民',
        defaults={'role_type': 'resident', 'permissions': {'can_view_work_orders': True}}
    )
    
    # 创建多个测试用户
    users_data = [
        {
            'username': 'user1',
            'phone': '13800138001',
            'password': 'password123',
            'role_id': resident_role.id
        },
        {
            'username': 'user2',
            'phone': '13800138002',
            'password': 'password123',
            'role_id': resident_role.id
        },
        {
            'username': 'test_admin',
            'phone': '13800138003',
            'password': 'admin123',
            'role_id': admin_role.id,
            'is_staff': True
        }
    ]
    
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(**user_data)
            print(f"创建用户成功: {user.username}")
        else:
            print(f"用户已存在: {user_data['username']}")

if __name__ == '__main__':
    create_test_users()