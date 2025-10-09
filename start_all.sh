#!/bin/bash

# AI-Kline 完整服务启动脚本 (MCP + Web)
# 使用方法: ./start_all.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline 完整服务启动脚本 ===${NC}"

# 检查是否在正确的目录
if [ ! -f "mcp_server.py" ] || [ ! -f "web_app.py" ]; then
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
if ! python -c "import openai, flask" 2>/dev/null; then
    echo -e "${YELLOW}安装项目依赖...${NC}"
    pip install -r requirements.txt
fi

# 设置环境变量
export MPLBACKEND=Agg
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export FLASK_APP=web_app.py
export FLASK_ENV=development

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}警告: 未设置 OPENAI_API_KEY 环境变量${NC}"
    echo -e "${YELLOW}请设置: export OPENAI_API_KEY='your-api-key'${NC}"
fi

# 确保输出目录存在
mkdir -p ./output/charts

# 函数：清理子进程
cleanup() {
    echo -e "\n${YELLOW}正在停止服务...${NC}"
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null || true
    fi
    if [ ! -z "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 启动 MCP 服务
echo -e "${BLUE}启动 MCP 服务...${NC}"
python mcp_server.py &
MCP_PID=$!

# 等待 MCP 服务启动
sleep 3

# 启动 Web 应用
echo -e "${BLUE}启动 Web 应用...${NC}"
python web_app.py &
WEB_PID=$!

echo ""
echo -e "${GREEN}=== 服务启动完成 ===${NC}"
echo -e "${YELLOW}MCP 服务: 运行中 (PID: $MCP_PID)${NC}"
echo -e "${YELLOW}Web 应用: http://localhost:5000 (PID: $WEB_PID)${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 等待用户中断
wait
