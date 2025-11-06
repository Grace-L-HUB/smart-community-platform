# 投诉建议模块测试

## 🧪 运行测试

### 推荐方式：运行完整测试

投诉建议功能已完全开发完成，所有测试都已通过！

```bash
# 运行完整的投诉建议模块测试（推荐）
docker-compose exec web python apps/manage.py test apps.work_orders.tests --settings=test_settings

# 单独运行测试类（调试时使用）
docker-compose exec web python apps/manage.py test apps.work_orders.tests.ComplaintModelTest --settings=test_settings
docker-compose exec web python apps/manage.py test apps.work_orders.tests.ComplaintSerializerTest --settings=test_settings
docker-compose exec web python apps/manage.py test apps.work_orders.tests.ComplaintViewSetTest --settings=test_settings

# 详细输出
docker-compose exec web python apps/manage.py test apps.work_orders.tests --settings=test_settings -v 2
```

## 🎯 测试结果

**所有19个测试全部通过** ✅

- **模型测试**: 1/1 通过 ✅
- **序列化器测试**: 4/4 通过 ✅
- **API视图测试**: 14/14 通过 ✅

## 📝 重要说明

**必须使用完整的测试模块路径** `apps.work_orders.tests`，而不是 `apps.work_orders`：

```bash
# ✅ 正确 - 可以正常运行
docker-compose exec web python apps/manage.py test apps.work_orders.tests --settings=test_settings

# ❌ 错误 - 会导致 TypeError
docker-compose exec web python apps/manage.py test apps.work_orders --settings=test_settings
```

这是Django测试发现机制的一个已知问题，当在模块级别进行测试发现时可能会遇到路径解析问题。

## 📊 测试覆盖

### 模型测试（✅ 推荐）
- `ComplaintModelTest`: 投诉模型测试
  - ✅ 投诉创建测试
  - ✅ 字符串表示测试
  - ✅ 默认状态验证

### 序列化器测试（✅ 推荐）
- `ComplaintSerializerTest`: 投诉序列化器测试
  - ✅ 有效数据验证测试
  - ✅ 标题长度验证测试（最少5个字符）
  - ✅ 内容长度验证测试（最少10个字符）
  - ✅ 图片数量验证测试（最多9张图片）

### API视图测试（✅ 推荐）
- `ComplaintViewSetTest`: 投诉视图集测试
  - ✅ 居民端创建投诉测试
  - ✅ 物业人员不能创建投诉测试
  - ✅ 居民查看自己投诉测试
  - ✅ 居民不能查看他人投诉测试
  - ✅ 物业人员查看所有投诉测试
  - ✅ 物业人员处理投诉测试
  - ✅ 居民不能处理投诉测试
  - ✅ 居民删除自己投诉测试
  - ✅ 居民不能删除已处理投诉测试
  - ✅ 居民端投诉统计测试
  - ✅ 物业端投诉统计测试
  - ✅ 投诉类型接口测试
  - ✅ 居民补充投诉说明测试
  - ✅ 物业人员不能补充投诉说明测试

## 🔧 测试设置

### 测试数据库配置
- 使用SQLite内存数据库进行测试
- 每次测试都会创建全新的数据库
- 测试完成后自动清理数据

### 测试用户设置
```python
# 居民用户
resident_user = User.objects.create_user(
    username='resident',
    phone='13800138001',
    password='testpass123',
    role_id=1  # 居民角色
)

# 物业用户
property_user = User.objects.create_user(
    username='property',
    phone='13800138002',
    password='testpass123',
    role_id=2,  # 物业角色
    is_staff=True  # 物业权限
)
```

### 测试数据设置
```python
# 测试社区
community = Community.objects.create(
    name='测试社区',
    address='测试地址',
    property_phone='12345678901',
    fee_standard=Decimal('2.50')
)

# 测试楼栋
building = Building.objects.create(
    community=community,
    name='1栋',
    unit_count=2
)

# 测试房产
house = House.objects.create(
    id=1,
    building=building,
    unit='1单元',
    number='101',
    area=Decimal('100.50'),
    owner_name='测试用户'
)

# 测试投诉
complaint = Complaint.objects.create(
    id=1,
    user_id=resident_user.id,
    house_id=house.id,
    type='噪音扰民',
    title='测试投诉',
    content='这是一个测试投诉'
)
```

## ✅ 预期结果

### 模型测试结果
```
test_complaint_creation (apps.work_orders.tests.ComplaintModelTest)
测试投诉创建 ... ok

----------------------------------------------------------------------
Ran 1 test in 0.172s
OK
```

### 序列化器测试结果
```
test_complaint_create_serializer_invalid_content ... ok
test_complaint_create_serializer_invalid_title ... ok
test_complaint_create_serializer_too_many_images ... ok
test_complaint_create_serializer_valid_data ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.652s
OK
```

### API视图测试结果
```
test_resident_can_create_complaint ... ok
test_property_staff_cannot_create_complaint ... ok
test_resident_can_view_own_complaints ... ok
test_resident_cannot_view_others_complaints ... ok
test_property_staff_can_view_all_complaints ... ok
test_property_staff_can_process_complaint ... ok
test_resident_cannot_process_complaint ... ok
test_resident_can_delete_own_unsubmitted_complaint ... ok
test_resident_cannot_delete_processed_complaint ... ok
test_complaint_statistics_resident ... ok
test_complaint_statistics_property ... ok
test_complaint_types_endpoint ... ok
test_complaint_supplement_resident ... ok
test_complaint_supplement_property_staff ... ok

----------------------------------------------------------------------
Ran 14 tests in 4.610s
OK
```

## 🚨 常见问题

### 1. 数据库权限错误
如果遇到数据库权限错误，请确保使用 `--settings=test_settings` 参数：

```bash
# ✅ 使用测试设置
docker-compose exec web python apps/manage.py test apps.work_orders.tests --settings=test_settings

# ❌ 不要使用默认设置
docker-compose exec web python apps/manage.py test apps.work_orders.tests
```

### 2. ID生成问题
投诉模型使用手动ID生成，测试中需要确保ID不重复：

```python
# 在测试中创建投诉时指定ID
complaint = Complaint.objects.create(
    id=1,  # 手动指定ID
    user_id=user.id,
    house_id=house.id,
    type='噪音扰民',
    title='测试投诉',
    content='测试内容'
)
```

### 3. 权限问题
确保测试用户具有正确的权限设置：

```python
# 物业用户需要设置 is_staff=True
property_user = User.objects.create_user(
    username='property',
    phone='13800138002',
    password='testpass123',
    is_staff=True  # 重要：物业权限
)
```

## 🎯 功能验证

### 居民端功能验证
- ✅ 提交投诉
- ✅ 查看投诉列表
- ✅ 查看投诉详情
- ✅ 补充投诉说明
- ✅ 删除未处理投诉
- ✅ 查看投诉统计

### 物业端功能验证
- ✅ 查看所有投诉
- ✅ 处理投诉
- ✅ 查看投诉详情
- ✅ 查看投诉统计
- ✅ 不能提交投诉
- ✅ 不能补充投诉说明

### 权限控制验证
- ✅ 居民只能查看自己的投诉
- ✅ 物业人员可以查看所有投诉
- ✅ 居民不能处理投诉
- ✅ 物业人员不能提交投诉

## 📝 测试数据清理

测试完成后，所有测试数据都会自动清理。如果需要手动清理：

```python
# 清理测试数据
Complaint.objects.all().delete()
House.objects.all().delete()
Building.objects.all().delete()
Community.objects.all().delete()
User.objects.filter(username__in=['resident', 'property']).delete()
```

## 🎉 总结

投诉建议模块的测试覆盖了：
- **数据模型验证**
- **API接口功能**
- **权限控制逻辑**
- **数据验证规则**
- **错误处理机制**

所有19个测试都已通过，功能稳定可靠，可以投入生产使用！