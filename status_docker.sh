#!/bin/bash

# AI-Kline Docker Compose 状态检查脚本
# 使用方法: ./status_docker.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline Docker Compose 状态检查 ===${NC}"
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误: 请在 AI-Kline 项目根目录下运行此脚本${NC}"
    exit 1
fi

# 检查容器状态
echo -e "${BLUE}=== 容器状态 ===${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}=== 服务端点 ===${NC}"

# 检查各个服务的健康状态
check_service() {
    local name=$1
    local url=$2
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name${NC}  - $url"
    else
        echo -e "${RED}✗ $name${NC}  - $url"
    fi
}

# 检查端口是否开放
check_port() {
    local name=$1
    local port=$2
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✓ $name${NC} - 端口 $port 正在监听"
    else
        echo -e "${RED}✗ $name${NC} - 端口 $port 未监听"
    fi
}

# 检查端口状态
check_port "MCP 服务" "20020"
check_port "MinIO API" "20021"
check_port "MinIO 控制台" "20022"

echo ""
echo -e "${BLUE}=== 访问地址 ===${NC}"
echo -e "${YELLOW}MCP 服务:${NC}     http://localhost:20020"
echo -e "${YELLOW}MinIO API:${NC}     http://localhost:20021"
echo -e "${YELLOW}MinIO 控制台:${NC}   http://localhost:20022"
echo -e "${YELLOW}Web 应用:${NC}      http://localhost:20023"

echo ""
echo -e "${BLUE}=== 资源使用 ===${NC}"
docker stats --no-stream $(docker-compose ps -q) 2>/dev/null || echo "无运行中的容器"

echo ""
echo -e "${BLUE}=== 最近日志 ===${NC}"
echo "MCP 服务日志:"
docker-compose logs --tail=5 ai-kline 2>/dev/null || echo "无日志"

echo ""
echo "MinIO 日志:"
docker-compose logs --tail=5 minio 2>/dev/null || echo "无日志"

echo ""
echo -e "${GREEN}状态检查完成${NC}"

