#!/bin/bash

# AI-Kline Docker Compose 启动脚本
# 使用方法: ./start_docker.sh [profile]
# 示例: ./start_docker.sh web

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline Docker Compose 启动脚本 ===${NC}"

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误: 请在 AI-Kline 项目根目录下运行此脚本${NC}"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker 未运行或无法访问${NC}"
    echo -e "${YELLOW}请启动 Docker Desktop 或 Docker 守护进程${NC}"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: docker-compose 未安装${NC}"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: .env 文件不存在${NC}"
    echo -e "${YELLOW}从 env.example 创建 .env 文件...${NC}"
    cp env.example .env
    echo -e "${YELLOW}请编辑 .env 文件配置必要的环境变量${NC}"
fi

# 检查必要的环境变量
if [ -f ".env" ]; then
    source .env
    if [ -z "$AI_KLINE_API_KEY" ] || [ "$AI_KLINE_API_KEY" = "your_api_key_here" ]; then
        echo -e "${RED}错误: 请配置 AI_KLINE_API_KEY 环境变量${NC}"
        echo -e "${YELLOW}编辑 .env 文件并设置 AI_KLINE_API_KEY${NC}"
        exit 1
    fi
fi

# 确定要启动的服务
PROFILE=""
if [ "$1" = "web" ]; then
    PROFILE="--profile web"
    echo -e "${BLUE}启动模式: 包含 Web 应用${NC}"
elif [ "$1" = "nginx" ]; then
    PROFILE="--profile web --profile nginx"
    echo -e "${BLUE}启动模式: 包含 Web 应用和 Nginx${NC}"
elif [ "$1" = "dev" ]; then
    echo -e "${BLUE}启动模式: 开发环境${NC}"
    echo -e "${YELLOW}启动开发环境...${NC}"
    docker-compose -f docker-compose.dev.yml up -d
    exit 0
else
    PROFILE=""
    echo -e "${BLUE}启动模式: 基础服务 (MCP + MinIO)${NC}"
fi

# 检查是否已有容器在运行
if docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}检测到已有容器在运行${NC}"
    echo -e "${YELLOW}如需重启，请先运行: ./stop_docker.sh${NC}"
    echo ""
    echo -e "${BLUE}当前容器状态:${NC}"
    docker-compose ps
    exit 0
fi

# 启动服务
echo -e "${GREEN}正在启动 Docker Compose 服务...${NC}"
if [ -n "$PROFILE" ]; then
    echo -e "${YELLOW}使用 profiles: $PROFILE${NC}"
    docker-compose $PROFILE up -d --build
else
    docker-compose up -d --build
fi

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 3

# 检查服务状态
echo ""
echo -e "${GREEN}=== 服务状态 ===${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}=== 访问信息 ===${NC}"
echo -e "${BLUE}MCP 服务:${NC}      http://localhost:20020"
echo -e "${BLUE}MinIO API:${NC}      http://localhost:20021"
echo -e "${BLUE}MinIO 控制台:${NC}  http://localhost:20022 (minioadmin/minioadmin)"

if echo "$PROFILE" | grep -q "web"; then
    echo -e "${BLUE}Web 应用:${NC}     http://localhost:20023"
fi

if echo "$PROFILE" | grep -q "nginx"; then
    echo -e "${BLUE}Nginx HTTP:${NC}   http://localhost:20024"
    echo -e "${BLUE}Nginx HTTPS:${NC}  https://localhost:20025"
fi

echo ""
echo -e "${GREEN}=== 管理命令 ===${NC}"
echo -e "${YELLOW}查看日志:${NC}     docker-compose logs -f"
echo -e "${YELLOW}停止服务:${NC}     ./stop_docker.sh"
echo -e "${YELLOW}重启服务:${NC}     ./restart_docker.sh"
echo -e "${YELLOW}查看状态:${NC}     ./status_docker.sh"

echo ""
echo -e "${GREEN}服务已成功启动！${NC}"

