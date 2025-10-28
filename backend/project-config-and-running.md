# 智能社区平台 - 项目配置与运行指南

本文档详细介绍了智能社区平台项目的配置与运行步骤，适用于开发团队成员快速搭建开发环境。

## 1. 环境要求

### 1.1 基础环境
- **操作系统**：Windows 10/11、macOS、Linux
- **Docker**：[Docker Desktop](https://www.docker.com/products/docker-desktop) (版本20.10或更高)
- **Git**：用于代码管理
- **推荐IDE**：
  - 后端：PyCharm、VS Code
  - 前端：VS Code + Vue插件
  - 小程序：微信开发者工具

### 1.2 系统资源要求
- **CPU**：至少4核
- **内存**：至少8GB RAM
- **磁盘空间**：至少20GB可用空间

## 2. 项目结构概览
Trae




思考过程
智能社区平台 - 项目配置与运行指南
本文档详细介绍了智能社区平台项目的配置与运行步骤，适用于开发团队成员快速搭建开发环境。

1. 环境要求
1.1 基础环境
操作系统：Windows 10/11、macOS、Linux
Docker：Docker Desktop (版本20.10或更高)
Git：用于代码管理
推荐IDE：
后端：PyCharm、VS Code
前端：VS Code + Vue插件
小程序：微信开发者工具
1.2 系统资源要求
CPU：至少4核
内存：至少8GB RAM
磁盘空间：至少20GB可用空间
2. 项目结构概览
PlainText



smart-community-platform/
├── backend/           # Django后端项目
├── frontend/          # Vue前端项目
├── miniapp/           # 微信小程序项目
├── media/             # 项目媒体资源
└── function-table.md  # 功能需求表


## 3. 后端环境配置

### 3.1 克隆项目代码

```bash
# 克隆项目仓库
git clone <项目仓库URL> smart-community-platform
cd smart-community-platform/backend
```

### 3.2 创建环境配置文件

```bash
# 复制环境变量示例文件
cp .env.example .env

# Windows系统可以使用以下命令
copy .env.example .env
```

### 3.3 配置环境变量

编辑`.env`文件，配置以下参数（开发环境可使用默认值）：
#### 数据库配置
DB_NAME=smart_community
DB_USER=root
DB_PASSWORD=123456
DB_HOST=db
DB_PORT=3306

#### Redis配置
REDIS_HOST=redis
REDIS_PORT=6379

#### Django配置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*

**注意**：生产环境部署时，请务必修改`SECRET_KEY`为强随机密钥，并调整`DEBUG`和`ALLOWED_HOSTS`配置。

### 3.4 使用Docker启动后端服务

确保Docker Desktop已启动，然后执行启动脚本：

**Windows系统**：
```bash
# 在backend目录下执行
.\start-docker.bat
```

**macOS/Linux系统**：
```bash
# 在backend目录下执行
chmod +x start-docker.sh  # 如存在启动脚本
./start-docker.sh
```

**手动启动方式**：
```bash
# 停止并移除现有容器（如需）
docker-compose down

# 构建并启动容器
docker-compose up -d --build

# 等待数据库就绪
# 运行数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser
```

## 4. 验证后端服务

服务启动后，可以通过以下URL访问验证：

- **管理后台**：http://localhost:8000/admin/ (使用创建的超级用户登录)
- **API文档**：http://localhost:8000/swagger/ (如已配置)
- **健康检查**：http://localhost:8000/health/

## 5. 前端环境配置（可选）

### 5.1 安装依赖

```bash
cd ../frontend/smart-community-platform
npm install
```

### 5.2 启动前端开发服务器

```bash
npm run dev
```

前端服务默认运行在 http://localhost:5173/

## 6. 微信小程序配置（可选）

### 6.1 导入项目

1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择`miniapp`目录
4. 使用测试账号或注册开发者账号登录

### 6.2 配置云开发环境

参考`miniapp/README.md`中的说明进行配置。

## 7. 常用Docker命令

### 7.1 查看服务状态

```bash
docker-compose ps
```

### 7.2 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志，例如web服务
docker-compose logs web

# 实时查看日志
docker-compose logs -f
```

### 7.3 停止服务

```bash
docker-compose stop
```

### 7.4 停止并移除服务

```bash
docker-compose down
```

### 7.5 重启服务

```bash
docker-compose restart
```

### 7.6 进入容器

```bash
# 进入web容器
docker-compose exec web bash
```

## 8. 开发注意事项

### 8.1 代码同步

修改代码后，对于后端服务，Docker会自动重新加载（开发模式）。如需重新构建镜像，请使用：

```bash
docker-compose up -d --build
```

### 8.2 数据库操作

- **创建新的模型**：修改models.py后，运行`makemigrations`和`migrate`命令
- **导入/导出数据**：使用Django的数据导入/导出工具

### 8.3 常见问题排查

1. **端口占用**：确保8000、3306、6379端口未被占用
2. **环境变量错误**：检查.env文件配置是否正确
3. **Docker权限**：确保当前用户有Docker执行权限
4. **网络连接**：容器间通信问题请检查docker-compose.yml中的网络配置

## 9. 团队协作规范

### 9.1 代码提交规范

- **分支命名**：`feature/功能名称`或`bugfix/问题描述`
- **提交信息**：清晰描述变更内容
- **代码审查**：重要变更需要团队成员审查

### 9.2 开发流程

1. 拉取最新代码
2. 创建功能分支
3. 完成开发并本地测试
4. 提交代码并创建合并请求
5. 团队审查通过后合并

## 10. 联系方式

如有问题，请联系项目负责人或在项目群中讨论。

---

*本文档会根据项目进展持续更新*```