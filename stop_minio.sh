#!/bin/bash

# AI-Kline MinIO 服务停止脚本
# 使用方法: ./stop_minio.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline MinIO 服务停止脚本 ===${NC}"

# 停止 MinIO 服务
echo -e "${YELLOW}停止 MinIO 服务...${NC}"
MINIO_PID_FILE="./logs/minio.pid"
if [ -f "$MINIO_PID_FILE" ]; then
    MINIO_PID=$(cat "$MINIO_PID_FILE")
    if ps -p "$MINIO_PID" > /dev/null 2>&1; then
        kill "$MINIO_PID"
        echo -e "${GREEN}MinIO 服务已停止 (PID: $MINIO_PID)${NC}"
    else
        echo -e "${YELLOW}MinIO 服务进程不存在，清理 PID 文件${NC}"
    fi
    rm -f "$MINIO_PID_FILE"
else
    # 备用方法：通过进程名查找
    MINIO_PIDS=$(pgrep -f "minio server")
    if [ ! -z "$MINIO_PIDS" ]; then
        echo "$MINIO_PIDS" | xargs kill
        echo -e "${GREEN}MinIO 服务已停止${NC}"
    else
        echo -e "${YELLOW}未找到运行中的 MinIO 服务${NC}"
    fi
fi

# 检查端口
MINIO_PORT=9000
if lsof -Pi :$MINIO_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    PORT_PID=$(lsof -t -i:$MINIO_PORT)
    echo -e "${YELLOW}端口 $MINIO_PORT 仍被占用 (PID: $PORT_PID)，尝试强制停止...${NC}"
    kill -9 $PORT_PID 2>/dev/null || true
fi

MINIO_CONSOLE_PORT=9001
if lsof -Pi :$MINIO_CONSOLE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    PORT_PID=$(lsof -t -i:$MINIO_CONSOLE_PORT)
    echo -e "${YELLOW}端口 $MINIO_CONSOLE_PORT 仍被占用 (PID: $PORT_PID)，尝试强制停止...${NC}"
    kill -9 $PORT_PID 2>/dev/null || true
fi

echo -e "${GREEN}MinIO 服务已完全停止${NC}"

