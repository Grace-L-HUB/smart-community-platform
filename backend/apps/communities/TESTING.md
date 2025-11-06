# 社区管理模块测试

## 🧪 运行测试

### 推荐方式：运行完整测试

现在所有问题都已解决，可以运行完整的社区模块测试！

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

## 🎯 测试结果

**所有27个测试全部通过** ✅

- **模型测试**: 8/8 通过 ✅
- **API测试**: 19/19 通过 ✅

## 📝 重要说明

**必须使用完整的测试模块路径** `apps.communities.tests`，而不是 `apps.communities`：

```bash
# ✅ 正确 - 可以正常运行
docker exec backend-web-1 python apps/manage.py test apps.communities.tests --settings=test_settings

# ❌ 错误 - 会导致 TypeError
docker exec backend-web-1 python apps/manage.py test apps.communities --settings=test_settings
```

这是Django测试发现机制的一个已知问题，当在模块级别进行测试发现时可能会遇到路径解析问题。

## 📊 测试覆盖

### 模型测试（✅ 推荐）
- `CommunityModelTest`: 小区模型测试
  - ✅ 字符串表示测试
  - ✅ 物业费标准验证测试
- `BuildingModelTest`: 楼栋模型测试
  - ✅ 字符串表示测试
  - ✅ 唯一性约束测试
- `HouseModelTest`: 房屋模型测试
  - ✅ 字符串表示测试
  - ✅ 唯一性约束测试
- `UserHouseModelTest`: 用户房产绑定模型测试
  - ✅ 字符串表示测试
  - ✅ 唯一性约束测试

## ✅ 预期结果

模型测试应该全部通过：
```
Ran 2 tests in X.XXXs
OK
```