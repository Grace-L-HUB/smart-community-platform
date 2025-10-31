@echo off
chcp 65001 >nul

REM Smart Community Platform - Docker Development Environment Startup Script
REM This script is used to quickly start the development environment on Windows

set "DOCKER_COMPOSE_FILE=docker-compose.yml"

REM Stop and remove existing containers
echo Stopping and cleaning existing containers...
docker-compose -f %DOCKER_COMPOSE_FILE% down -v

REM Build and start new containers
echo Building and starting new Docker containers...
docker-compose -f %DOCKER_COMPOSE_FILE% up -d --build

REM Wait for database service to be ready
echo Waiting for MySQL database service to be ready...
ping -n 10 127.0.0.1 > nul

REM Run database migrations
echo Running database migrations...
docker-compose -f %DOCKER_COMPOSE_FILE% exec web python apps/manage.py migrate

REM Create superuser (if not exists)
echo Creating superuser...
docker-compose -f %DOCKER_COMPOSE_FILE% exec -e DJANGO_SUPERUSER_USERNAME=admin -e DJANGO_SUPERUSER_EMAIL=admin@example.com -e DJANGO_SUPERUSER_PASSWORD=admin123456 web python apps/manage.py createsuperuser --noinput || echo Superuser may already exist or creation failed

REM Display service information
echo Development environment started successfully!
echo ====================================================
echo Access URLs:
echo - Admin Panel: http://localhost:8000/admin/
echo - API Documentation: http://localhost:8000/swagger/
echo - Health Check: http://localhost:8000/health/
echo ====================================================
echo To view logs, run: docker-compose -f %DOCKER_COMPOSE_FILE% logs -f
echo To stop services, run: docker-compose -f %DOCKER_COMPOSE_FILE% down
echo ====================================================

REM 保持窗口打开
pause