#!/bin/bash

# AI-Kline Docker Compose 停止脚本
# 使用方法: ./stop_docker.sh [--remove-volumes]

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline Docker Compose 停止脚本 ===${NC}"

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误: 请在 AI-Kline 项目根目录下运行此脚本${NC}"
    exit 1
fi

# 检查容器状态
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}未找到运行中的容器${NC}"
    exit 0
fi

echo -e "${YELLOW}正在停止 Docker Compose 服务...${NC}"

# 停止所有服务
if [ "$1" = "--remove-volumes" ]; then
    echo -e "${YELLOW}将删除数据卷...${NC}"
    docker-compose down -v
    echo -e "${GREEN}已停止服务并删除数据卷${NC}"
else
    docker-compose down
    echo -e "${GREEN}已停止服务${NC}"
fi

# 检查是否还有容器
if docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}仍有容器在运行:${NC}"
    docker-compose ps
else
    echo -e "${GREEN}所有服务已停止${NC}"
fi

