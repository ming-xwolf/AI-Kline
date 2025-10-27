#!/bin/bash

# AI-Kline MinIO 服务启动脚本
# 使用方法: ./start_minio.sh
# 注意: 此脚本启动 MinIO 服务，用于存储 AI-Kline 生成的图表

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline MinIO 服务启动脚本 ===${NC}"

# 检查 MinIO 是否已安装
if ! command -v minio &> /dev/null; then
    echo -e "${RED}错误: MinIO 未安装${NC}"
    echo -e "${YELLOW}请安装 MinIO:${NC}"
    echo -e "${BLUE}# macOS: brew install minio/stable/minio${NC}"
    echo -e "${BLUE}# Linux: wget https://dl.min.io/server/minio/release/linux-amd64/minio && chmod +x minio${NC}"
    echo -e "${BLUE}# 或使用 Docker: docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address :9001${NC}"
    exit 1
fi

# 设置 MinIO 数据目录
MINIO_DATA_DIR="${HOME}/minio-data"
MINIO_CONSOLE_PORT=9001
MINIO_PORT=9000

# 创建数据目录
if [ ! -d "$MINIO_DATA_DIR" ]; then
    echo -e "${YELLOW}创建 MinIO 数据目录: $MINIO_DATA_DIR${NC}"
    mkdir -p "$MINIO_DATA_DIR"
fi

# 确保日志目录存在
mkdir -p ./logs

# 生成日志文件名（包含时间戳）
LOG_FILE="./logs/minio_$(date +%Y%m%d_%H%M%S).log"
PID_FILE="./logs/minio.pid"

# 检查是否已有 MinIO 服务在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}检测到 MinIO 服务已在运行 (PID: $OLD_PID)${NC}"
        echo -e "${YELLOW}如需重启，请先运行: ./stop_minio.sh${NC}"
        exit 1
    else
        echo -e "${YELLOW}清理旧的 PID 文件...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# 检查端口是否被占用
if lsof -Pi :$MINIO_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}错误: 端口 $MINIO_PORT 已被占用${NC}"
    echo -e "${YELLOW}请先停止占用该端口的服务${NC}"
    exit 1
fi

# 启动 MinIO 服务（后台运行）
echo -e "${GREEN}启动 MinIO 服务...${NC}"
echo -e "${YELLOW}数据目录: $MINIO_DATA_DIR${NC}"
echo -e "${YELLOW}API 端口: $MINIO_PORT${NC}"
echo -e "${YELLOW}控制台端口: $MINIO_CONSOLE_PORT${NC}"
echo -e "${YELLOW}日志文件: $LOG_FILE${NC}"
echo -e "${YELLOW}PID 文件: $PID_FILE${NC}"
echo ""
echo -e "${BLUE}访问 MinIO 控制台: http://localhost:$MINIO_CONSOLE_PORT${NC}"
echo -e "${BLUE}默认凭证: minioadmin / minioadmin${NC}"
echo -e "${YELLOW}使用 ./stop_minio.sh 停止服务${NC}"
echo ""

# 后台启动并保存 PID
nohup minio server "$MINIO_DATA_DIR" \
    --console-address ":$MINIO_CONSOLE_PORT" \
    > "$LOG_FILE" 2>&1 &
MINIO_PID=$!
echo $MINIO_PID > "$PID_FILE"

echo -e "${GREEN}MinIO 服务已启动 (PID: $MINIO_PID)${NC}"
echo -e "${YELLOW}查看日志: tail -f $LOG_FILE${NC}"
echo ""

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 2

# 检查服务是否成功启动
if ps -p "$MINIO_PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MinIO 服务运行正常${NC}"
    echo -e "${GREEN}✓ API 端点: http://localhost:$MINIO_PORT${NC}"
    echo -e "${GREEN}✓ 控制台: http://localhost:$MINIO_CONSOLE_PORT${NC}"
    echo ""
    echo -e "${BLUE}在 .env 文件中配置 MinIO 连接:${NC}"
    echo -e "MINIO_ENDPOINT=localhost"
    echo -e "MINIO_PORT=9000"
    echo -e "MINIO_USE_SSL=false"
    echo -e "MINIO_ACCESS_KEY=minioadmin"
    echo -e "MINIO_SECRET_KEY=minioadmin"
    echo -e "MINIO_BUCKET_NAME=ai-kline-charts"
else
    echo -e "${RED}✗ MinIO 服务启动失败${NC}"
    echo -e "${RED}请查看日志: $LOG_FILE${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

