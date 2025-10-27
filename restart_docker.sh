#!/bin/bash

# AI-Kline Docker Compose 重启脚本
# 使用方法: ./restart_docker.sh [profile]

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline Docker Compose 重启脚本 ===${NC}"

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误: 请在 AI-Kline 项目根目录下运行此脚本${NC}"
    exit 1
fi

# 停止服务
echo -e "${YELLOW}步骤 1/2: 停止现有服务...${NC}"
docker-compose down

# 启动服务
echo -e "${YELLOW}步骤 2/2: 启动服务...${NC}"
if [ "$1" = "web" ]; then
    docker-compose --profile web up -d --build
elif [ "$1" = "nginx" ]; then
    docker-compose --profile web --profile nginx up -d --build
else
    docker-compose up -d --build
fi

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 3

echo ""
echo -e "${GREEN}=== 服务状态 ===${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}服务已重启！${NC}"

