#!/bin/bash

# AI-Kline 服务状态检查脚本
# 使用方法: ./check_status.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI-Kline 服务状态检查 ===${NC}"

# 检查 conda 环境
echo -e "${BLUE}检查 conda 环境...${NC}"
if conda info --envs | grep -q "AI-Kline"; then
    echo -e "${GREEN}✓ AI-Kline conda 环境存在${NC}"
else
    echo -e "${RED}✗ AI-Kline conda 环境不存在${NC}"
fi

# 检查 MCP 服务
echo -e "${BLUE}检查 MCP 服务...${NC}"
MCP_PID_FILE="./logs/mcp_server.pid"
if [ -f "$MCP_PID_FILE" ]; then
    MCP_PID=$(cat "$MCP_PID_FILE")
    if ps -p "$MCP_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ MCP 服务运行中 (PID: $MCP_PID)${NC}"
        echo -e "${YELLOW}  PID 文件: $MCP_PID_FILE${NC}"
    else
        echo -e "${RED}✗ MCP 服务进程不存在，但 PID 文件存在${NC}"
        echo -e "${YELLOW}  建议清理 PID 文件: rm $MCP_PID_FILE${NC}"
    fi
else
    # 备用检查方法
    MCP_PIDS=$(pgrep -f "python.*mcp_server.py")
    if [ ! -z "$MCP_PIDS" ]; then
        echo -e "${GREEN}✓ MCP 服务运行中 (PID: $MCP_PIDS) - 未使用 PID 文件管理${NC}"
    else
        echo -e "${RED}✗ MCP 服务未运行${NC}"
    fi
fi

# 检查 Web 应用
echo -e "${BLUE}检查 Web 应用...${NC}"
WEB_PID_FILE="./logs/web_app.pid"
if [ -f "$WEB_PID_FILE" ]; then
    WEB_PID=$(cat "$WEB_PID_FILE")
    if ps -p "$WEB_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Web 应用运行中 (PID: $WEB_PID)${NC}"
        echo -e "${YELLOW}  访问地址: http://localhost:5000${NC}"
        echo -e "${YELLOW}  PID 文件: $WEB_PID_FILE${NC}"
    else
        echo -e "${RED}✗ Web 应用进程不存在，但 PID 文件存在${NC}"
        echo -e "${YELLOW}  建议清理 PID 文件: rm $WEB_PID_FILE${NC}"
    fi
else
    # 备用检查方法
    WEB_PIDS=$(pgrep -f "python.*web_app.py")
    if [ ! -z "$WEB_PIDS" ]; then
        echo -e "${GREEN}✓ Web 应用运行中 (PID: $WEB_PIDS) - 未使用 PID 文件管理${NC}"
        echo -e "${YELLOW}  访问地址: http://localhost:5000${NC}"
    else
        echo -e "${RED}✗ Web 应用未运行${NC}"
    fi
fi

# 检查端口占用
echo -e "${BLUE}检查端口占用...${NC}"
if lsof -i :5000 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 端口 5000 被占用${NC}"
else
    echo -e "${YELLOW}○ 端口 5000 空闲${NC}"
fi

# 检查环境变量
echo -e "${BLUE}检查环境变量...${NC}"
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✓ OPENAI_API_KEY 已设置${NC}"
else
    echo -e "${RED}✗ OPENAI_API_KEY 未设置${NC}"
fi

if [ ! -z "$MPLBACKEND" ]; then
    echo -e "${GREEN}✓ MPLBACKEND 已设置: $MPLBACKEND${NC}"
else
    echo -e "${YELLOW}○ MPLBACKEND 未设置 (将使用默认值)${NC}"
fi

# 检查输出目录
echo -e "${BLUE}检查输出目录...${NC}"
if [ -d "./output" ]; then
    echo -e "${GREEN}✓ 输出目录存在${NC}"
    if [ -d "./output/charts" ]; then
        echo -e "${GREEN}✓ 图表目录存在${NC}"
    else
        echo -e "${YELLOW}○ 图表目录不存在${NC}"
    fi
else
    echo -e "${RED}✗ 输出目录不存在${NC}"
fi

# 检查日志目录
echo -e "${BLUE}检查日志目录...${NC}"
if [ -d "./logs" ]; then
    echo -e "${GREEN}✓ 日志目录存在${NC}"
    LOG_COUNT=$(ls -1 ./logs/*.log 2>/dev/null | wc -l)
    if [ "$LOG_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ 找到 $LOG_COUNT 个日志文件${NC}"
        echo -e "${YELLOW}  最新日志文件:${NC}"
        ls -lt ./logs/*.log 2>/dev/null | head -3 | awk '{print "    " $9 " (" $6 " " $7 " " $8 ")"}'
    else
        echo -e "${YELLOW}○ 日志目录为空${NC}"
    fi
else
    echo -e "${YELLOW}○ 日志目录不存在${NC}"
fi

echo ""
echo -e "${GREEN}=== 状态检查完成 ===${NC}"
