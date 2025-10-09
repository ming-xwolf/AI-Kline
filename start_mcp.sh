#!/bin/bash

# AI-Kline MCP 服务启动脚本
# 使用方法: ./start_mcp.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline MCP 服务启动脚本 ===${NC}"

# 检查是否在正确的目录
if [ ! -f "mcp_server.py" ]; then
    echo -e "${RED}错误: 请在 AI-Kline 项目根目录下运行此脚本${NC}"
    exit 1
fi

# 检查 conda 环境是否存在
if ! conda info --envs | grep -q "AI-Kline"; then
    echo -e "${YELLOW}警告: 未找到 AI-Kline conda 环境，正在创建...${NC}"
    conda create -n AI-Kline python=3.11 -y
    echo -e "${GREEN}AI-Kline 环境创建完成${NC}"
fi

# 激活 conda 环境
echo -e "${YELLOW}激活 conda 环境: AI-Kline${NC}"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate AI-Kline

# 检查并安装依赖
echo -e "${YELLOW}检查依赖包...${NC}"
if ! python -c "import openai" 2>/dev/null; then
    echo -e "${YELLOW}安装项目依赖...${NC}"
    pip install -r requirements.txt
fi

# 设置环境变量
export MPLBACKEND=Agg
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}警告: 未设置 OPENAI_API_KEY 环境变量${NC}"
    echo -e "${YELLOW}请设置: export OPENAI_API_KEY='your-api-key'${NC}"
fi

# 确保日志目录存在
mkdir -p ./logs

# 生成日志文件名（包含时间戳）
LOG_FILE="./logs/mcp_server_$(date +%Y%m%d_%H%M%S).log"
PID_FILE="./logs/mcp_server.pid"

# 检查是否已有服务在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}检测到 MCP 服务已在运行 (PID: $OLD_PID)${NC}"
        echo -e "${YELLOW}如需重启，请先运行: ./stop_services.sh${NC}"
        exit 1
    else
        echo -e "${YELLOW}清理旧的 PID 文件...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# 启动 MCP 服务（后台运行）
echo -e "${GREEN}启动 AI-Kline MCP 服务...${NC}"
echo -e "${YELLOW}日志文件: $LOG_FILE${NC}"
echo -e "${YELLOW}PID 文件: $PID_FILE${NC}"
echo -e "${YELLOW}使用 ./stop_services.sh 停止服务${NC}"
echo ""

# 后台启动并保存 PID
nohup python mcp_server.py > "$LOG_FILE" 2>&1 &
MCP_PID=$!
echo $MCP_PID > "$PID_FILE"

echo -e "${GREEN}MCP 服务已启动 (PID: $MCP_PID)${NC}"
echo -e "${YELLOW}查看日志: tail -f $LOG_FILE${NC}"
