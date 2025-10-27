#!/bin/bash

# AI-Kline MinIO 服务状态检查脚本
# 使用方法: ./check_minio.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline MinIO 服务状态检查 ===${NC}"
echo ""

# 检查 PID 文件
PID_FILE="./logs/minio.pid"
if [ -f "$PID_FILE" ]; then
    MINIO_PID=$(cat "$PID_FILE")
    if ps -p "$MINIO_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ MinIO 服务正在运行 (PID: $MINIO_PID)${NC}"
    else
        echo -e "${RED}✗ MinIO 服务进程不存在${NC}"
        rm -f "$PID_FILE"
    fi
else
    echo -e "${YELLOW}✗ MinIO 服务未启动${NC}"
fi

# 检查端口
echo ""
echo -e "${BLUE}检查端口状态:${NC}"
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001

if lsof -Pi :$MINIO_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 端口 $MINIO_PORT 正在监听 (API)${NC}"
else
    echo -e "${RED}✗ 端口 $MINIO_PORT 未监听${NC}"
fi

if lsof -Pi :$MINIO_CONSOLE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 端口 $MINIO_CONSOLE_PORT 正在监听 (控制台)${NC}"
else
    echo -e "${RED}✗ 端口 $MINIO_CONSOLE_PORT 未监听${NC}"
fi

# 检查日志文件
echo ""
echo -e "${BLUE}最近的日志文件:${NC}"
if [ -d "./logs" ]; then
    MINIO_LOGS=$(ls -t ./logs/minio_*.log 2>/dev/null | head -5)
    if [ ! -z "$MINIO_LOGS" ]; then
        for log in $MINIO_LOGS; do
            echo -e "${YELLOW}  $log${NC}"
        done
    else
        echo -e "${YELLOW}  未找到日志文件${NC}"
    fi
else
    echo -e "${YELLOW}  日志目录不存在${NC}"
fi

# 检查数据目录
echo ""
echo -e "${BLUE}MinIO 数据目录:${NC}"
MINIO_DATA_DIR="${HOME}/minio-data"
if [ -d "$MINIO_DATA_DIR" ]; then
    SIZE=$(du -sh "$MINIO_DATA_DIR" 2>/dev/null | cut -f1)
    FILE_COUNT=$(find "$MINIO_DATA_DIR" -type f 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ $MINIO_DATA_DIR${NC}"
    echo -e "${YELLOW}  大小: $SIZE${NC}"
    echo -e "${YELLOW}  文件数: $FILE_COUNT${NC}"
else
    echo -e "${YELLOW}✗ 数据目录不存在: $MINIO_DATA_DIR${NC}"
fi

# 检查环境变量配置
echo ""
echo -e "${BLUE}检查 .env 配置:${NC}"
if [ -f ".env" ]; then
    if grep -q "MINIO_" .env; then
        echo -e "${GREEN}✓ .env 文件包含 MinIO 配置${NC}"
        grep "MINIO_" .env | sed 's/=.*/=***/'
    else
        echo -e "${YELLOW}✗ .env 文件未包含 MinIO 配置${NC}"
    fi
else
    echo -e "${YELLOW}✗ .env 文件不存在${NC}"
    echo -e "${YELLOW}  使用 cp env.example .env 创建配置文件${NC}"
fi

# 总结
echo ""
echo -e "${BLUE}=== 访问信息 ===${NC}"
echo -e "${YELLOW}API 端点: http://localhost:9000${NC}"
echo -e "${YELLOW}控制台: http://localhost:9001${NC}"
echo -e "${YELLOW}默认凭证: minioadmin / minioadmin${NC}"

if [ -f "$PID_FILE" ] && ps -p "$MINIO_PID" > /dev/null 2>&1; then
    echo ""
    echo -e "${GREEN}状态: 运行中 ✓${NC}"
else
    echo ""
    echo -e "${YELLOW}状态: 未运行${NC}"
    echo -e "${YELLOW}使用 ./start_minio.sh 启动服务${NC}"
fi

