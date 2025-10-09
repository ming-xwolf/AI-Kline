#!/bin/bash

# AI-Kline 服务停止脚本
# 使用方法: ./stop_services.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline 服务停止脚本 ===${NC}"

# 停止 MCP 服务
echo -e "${YELLOW}停止 MCP 服务...${NC}"
MCP_PID_FILE="./logs/mcp_server.pid"
if [ -f "$MCP_PID_FILE" ]; then
    MCP_PID=$(cat "$MCP_PID_FILE")
    if ps -p "$MCP_PID" > /dev/null 2>&1; then
        kill "$MCP_PID"
        echo -e "${GREEN}MCP 服务已停止 (PID: $MCP_PID)${NC}"
    else
        echo -e "${YELLOW}MCP 服务进程不存在，清理 PID 文件${NC}"
    fi
    rm -f "$MCP_PID_FILE"
else
    # 备用方法：通过进程名查找
    MCP_PIDS=$(pgrep -f "python.*mcp_server.py")
    if [ ! -z "$MCP_PIDS" ]; then
        echo "$MCP_PIDS" | xargs kill
        echo -e "${GREEN}MCP 服务已停止${NC}"
    else
        echo -e "${YELLOW}未找到运行中的 MCP 服务${NC}"
    fi
fi

# 停止 Web 应用
echo -e "${YELLOW}停止 Web 应用...${NC}"
WEB_PID_FILE="./logs/web_app.pid"
if [ -f "$WEB_PID_FILE" ]; then
    WEB_PID=$(cat "$WEB_PID_FILE")
    if ps -p "$WEB_PID" > /dev/null 2>&1; then
        kill "$WEB_PID"
        echo -e "${GREEN}Web 应用已停止 (PID: $WEB_PID)${NC}"
    else
        echo -e "${YELLOW}Web 应用进程不存在，清理 PID 文件${NC}"
    fi
    rm -f "$WEB_PID_FILE"
else
    # 备用方法：通过进程名查找
    WEB_PIDS=$(pgrep -f "python.*web_app.py")
    if [ ! -z "$WEB_PIDS" ]; then
        echo "$WEB_PIDS" | xargs kill
        echo -e "${GREEN}Web 应用已停止${NC}"
    else
        echo -e "${YELLOW}未找到运行中的 Web 应用${NC}"
    fi
fi

# 停止所有相关 Python 进程
echo -e "${YELLOW}清理相关进程...${NC}"
PYTHON_PIDS=$(pgrep -f "AI-Kline")
if [ ! -z "$PYTHON_PIDS" ]; then
    echo "$PYTHON_PIDS" | xargs kill 2>/dev/null || true
fi

echo -e "${GREEN}所有服务已停止${NC}"
