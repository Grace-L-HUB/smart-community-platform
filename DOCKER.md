# Docker环境使用指南

## 环境要求

- Docker Desktop
- 至少4GB RAM
- Windows/macOS/Linux

## 首次启动

1. 确保Docker Desktop已启动
2. 打开命令行工具，进入backend目录
3. 运行启动脚本：

```bash
# Windows
start-docker.bat

# macOS/Linux
source start-docker.sh  # 如果已创建
```

或者手动执行以下命令：

```bash
docker-compose up --build
```

## 访问应用

- 应用地址：http://localhost:8000
- Django管理后台：http://localhost:8000/admin/
- API文档（Swagger）：http://localhost:8000/swagger/
- API文档（ReDoc）：http://localhost:8000/redoc/

## 常用命令

### 启动服务
```bash
docker-compose up
```

### 停止服务
```bash
docker-compose down
```

### 重新构建镜像
```bash
docker-compose up --build
```

### 运行数据库迁移
```bash
docker-compose exec web python apps/manage.py migrate
```

### 创建超级用户
```bash
docker-compose exec web python apps/manage.py createsuperuser
```

### 查看容器日志
```bash
docker-compose logs -f web  # 查看web服务日志
docker-compose logs -f db   # 查看数据库日志
```

### 进入容器内部
```bash
docker-compose exec web bash  # 进入web容器
```

## 注意事项

1. 代码更改会自动同步到容器中，无需重新构建
2. 数据库数据存储在卷中，停止容器不会丢失数据
3. 如需修改数据库配置，修改docker-compose.yml中的环境变量