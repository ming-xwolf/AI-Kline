#!/bin/bash

# AI-Kline 日志查看脚本
# 使用方法: ./view_logs.sh [service] [lines]
# 示例: ./view_logs.sh web 50
#       ./view_logs.sh mcp
#       ./view_logs.sh all

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE=${1:-"all"}
LINES=${2:-"50"}

echo -e "${GREEN}=== AI-Kline 日志查看工具 ===${NC}"

# 检查日志目录
if [ ! -d "./logs" ]; then
    echo -e "${RED}错误: 日志目录不存在${NC}"
    exit 1
fi

# 显示可用日志文件
echo -e "${BLUE}可用的日志文件:${NC}"
ls -lt ./logs/*.log 2>/dev/null | awk '{print "  " $9 " (" $6 " " $7 " " $8 ")"}'

echo ""

# 根据服务类型显示日志
case $SERVICE in
    "web")
        echo -e "${YELLOW}显示 Web 应用最新日志 (最后 $LINES 行):${NC}"
        WEB_LOG=$(ls -t ./logs/web_app_*.log 2>/dev/null | head -1)
        if [ -n "$WEB_LOG" ]; then
            echo -e "${GREEN}日志文件: $WEB_LOG${NC}"
            echo ""
            tail -n $LINES "$WEB_LOG"
        else
            echo -e "${RED}未找到 Web 应用日志文件${NC}"
        fi
        ;;
    "mcp")
        echo -e "${YELLOW}显示 MCP 服务最新日志 (最后 $LINES 行):${NC}"
        MCP_LOG=$(ls -t ./logs/mcp_server_*.log 2>/dev/null | head -1)
        if [ -n "$MCP_LOG" ]; then
            echo -e "${GREEN}日志文件: $MCP_LOG${NC}"
            echo ""
            tail -n $LINES "$MCP_LOG"
        else
            echo -e "${RED}未找到 MCP 服务日志文件${NC}"
        fi
        ;;
    "all")
        echo -e "${YELLOW}显示所有服务最新日志 (最后 $LINES 行):${NC}"
        
        # Web 应用日志
        WEB_LOG=$(ls -t ./logs/web_app_*.log 2>/dev/null | head -1)
        if [ -n "$WEB_LOG" ]; then
            echo -e "${GREEN}=== Web 应用日志: $WEB_LOG ===${NC}"
            tail -n $LINES "$WEB_LOG"
            echo ""
        fi
        
        # MCP 服务日志
        MCP_LOG=$(ls -t ./logs/mcp_server_*.log 2>/dev/null | head -1)
        if [ -n "$MCP_LOG" ]; then
            echo -e "${GREEN}=== MCP 服务日志: $MCP_LOG ===${NC}"
            tail -n $LINES "$MCP_LOG"
        fi
        ;;
    *)
        echo -e "${RED}错误: 无效的服务名称${NC}"
        echo -e "${YELLOW}使用方法:${NC}"
        echo -e "  ./view_logs.sh web [行数]    - 查看 Web 应用日志"
        echo -e "  ./view_logs.sh mcp [行数]    - 查看 MCP 服务日志"
        echo -e "  ./view_logs.sh all [行数]    - 查看所有日志"
        echo -e "  ./view_logs.sh               - 查看所有日志 (默认50行)"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}提示:${NC}"
echo -e "  - 实时查看日志: tail -f ./logs/[日志文件名]"
echo -e "  - 查看完整日志: cat ./logs/[日志文件名]"
echo -e "  - 搜索日志内容: grep '关键词' ./logs/*.log"
