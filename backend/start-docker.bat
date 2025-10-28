@echo off

REM 智慧社区平台 - Docker开发环境启动脚本
REM 此脚本用于在Windows环境下快速启动开发环境

set "DOCKER_COMPOSE_FILE=docker-compose.yml"

REM 停止并移除现有的容器
@echo 正在停止并清理现有的容器...
docker-compose -f %DOCKER_COMPOSE_FILE% down -v

REM 构建并启动新的容器
@echo 正在构建并启动新的Docker容器...
docker-compose -f %DOCKER_COMPOSE_FILE% up -d --build

REM 等待数据库服务就绪
@echo 等待MySQL数据库服务就绪...
ping -n 10 127.0.0.1 > nul

REM 运行数据库迁移
@echo 正在执行数据库迁移...
docker-compose -f %DOCKER_COMPOSE_FILE% exec web python apps/manage.py migrate

REM 创建超级用户（如果不存在）
@echo 正在创建超级用户...
docker-compose -f %DOCKER_COMPOSE_FILE% exec web python apps/manage.py createsuperuser --noinput || echo 超级用户可能已存在或创建失败

REM 显示服务信息
@echo 开发环境已成功启动！
@echo ====================================================
@echo 访问地址：
@echo - 管理后台：http://localhost:8000/admin/
@echo - API文档：http://localhost:8000/swagger/
@echo - 健康检查：http://localhost:8000/health/
@echo ====================================================
@echo 如需查看日志，请运行: docker-compose -f %DOCKER_COMPOSE_FILE% logs -f
@echo 如需停止服务，请运行: docker-compose -f %DOCKER_COMPOSE_FILE% down
@echo ====================================================

REM 保持窗口打开
pause