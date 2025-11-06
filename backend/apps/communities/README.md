# 社区管理模块

## 📋 功能概述

负责管理小区、楼栋、房屋等基础信息，以及用户房产绑定功能。

## 🏗️ 核心功能

### 数据模型
- **Community**: 小区信息（名称、地址、物业费标准）
- **Building**: 楼栋信息（名称、单元数）
- **House**: 房屋信息（房号、面积、业主）
- **UserHouse**: 用户房产绑定（申请、审核、权限）

### API接口
- 小区、楼栋、房屋的CRUD操作
- 用户房产绑定申请和审核流程
- 统计信息和自定义Action

## 🧪 测试

### 运行测试

```bash
# 运行完整的社区模块测试（推荐）
docker exec backend-web-1 python apps/manage.py test apps.communities.tests --settings=test_settings

# 单独运行测试类（调试时使用）
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.CommunityModelTest --settings=test_settings
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.BuildingModelTest --settings=test_settings
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.HouseModelTest --settings=test_settings
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.UserHouseModelTest --settings=test_settings

# API测试
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.CommunityAPITest --settings=test_settings
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.BuildingAPITest --settings=test_settings
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.HouseAPITest --settings=test_settings
docker exec backend-web-1 python apps/manage.py test apps.communities.tests.UserHouseAPITest --settings=test_settings

# 详细输出
docker exec backend-web-1 python apps/manage.py test apps.communities.tests --settings=test_settings -v 2
```

**重要提示**: 必须使用 `apps.communities.tests` 而不是 `apps.communities` 来运行测试，以避免Django测试发现的路径问题。

### 测试覆盖
- ✅ 模型验证测试
- ✅ API功能测试
- ✅ 权限控制测试
- ✅ 业务流程测试

详细测试说明请查看 [TESTING.md](./TESTING.md)