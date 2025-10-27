#!/bin/bash

# MinIO 访问策略配置脚本
# 用于设置 MinIO 存储桶的公共访问权限
# 
# 使用方法:
#   ./configure_minio_access.sh                          # 使用默认值
#   ./configure_minio_access.sh localhost 9000           # 指定 IP 和端口
#   ./configure_minio_access.sh localhost 20021          # Docker 模式

# 默认配置
DEFAULT_HOST=${1:-localhost}
DEFAULT_PORT=${2:-9000}
DEFAULT_BUCKET=${3:-ai-kline-charts}

# 从参数或环境变量获取配置
MINIO_HOST=${MINIO_HOST:-$DEFAULT_HOST}
MINIO_PORT=${MINIO_PORT:-$DEFAULT_PORT}
BUCKET_NAME=${BUCKET_NAME:-$DEFAULT_BUCKET}
MINIO_ALIAS=${MINIO_ALIAS:-ai-kline-local}

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MinIO 访问策略配置 ===${NC}"
echo -e "${BLUE}使用配置:${NC}"
echo -e "  主机: ${MINIO_HOST}"
echo -e "  端口: ${MINIO_PORT}"
echo -e "  存储桶: ${BUCKET_NAME}"
echo ""

# 检查 mc 命令是否安装
if ! command -v mc &> /dev/null; then
    echo -e "${YELLOW}mc 命令未安装，开始安装...${NC}"
    
    # 检测操作系统
    OS="$(uname -s)"
    case "${OS}" in
        Linux*)
            echo "下载 MinIO 客户端 (Linux)..."
            wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /tmp/mc
            chmod +x /tmp/mc
            sudo mv /tmp/mc /usr/local/bin/mc
            ;;
        Darwin*)
            echo "使用 Homebrew 安装..."
            if command -v brew &> /dev/null; then
                brew install minio/stable/mc
            else
                echo -e "${RED}请先安装 Homebrew 或手动安装 mc${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}不支持的操作系统: ${OS}${NC}"
            exit 1
            ;;
    esac
fi

# 配置别名
echo -e "${YELLOW}配置 MinIO 别名...${NC}"
MINIO_ENDPOINT="http://${MINIO_HOST}:${MINIO_PORT}"
mc alias set ${MINIO_ALIAS} ${MINIO_ENDPOINT} minioadmin minioadmin 2>/dev/null || \
mc alias set ${MINIO_ALIAS} ${MINIO_ENDPOINT} minioadmin minioadmin --api s3v4

# 检查存储桶是否存在
if ! mc ls ${MINIO_ALIAS}/${BUCKET_NAME} &> /dev/null; then
    echo -e "${YELLOW}创建存储桶: ${BUCKET_NAME}${NC}"
    mc mb ${MINIO_ALIAS}/${BUCKET_NAME}
fi

# 设置公共访问策略（只读）
echo -e "${YELLOW}设置公共访问策略（只读）...${NC}"

# 创建访问策略 JSON
POLICY_JSON=$(cat << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": ["*"]
            },
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::ai-kline-charts/*"]
        }
    ]
}
EOF
)

# 设置策略
echo "$POLICY_JSON" | mc anonymous set-json ${MINIO_ALIAS}/${BUCKET_NAME} stdin

# 或者使用简化的方法
echo -e "${YELLOW}设置公开下载权限...${NC}"
mc anonymous set download ${MINIO_ALIAS}/${BUCKET_NAME}/

echo -e "${GREEN}✓ MinIO 访问策略配置完成${NC}"

# 验证配置
echo -e "${YELLOW}验证配置...${NC}"
mc anonymous get ${MINIO_ALIAS}/${BUCKET_NAME}

echo ""
echo -e "${BLUE}现在可以通过以下 URL 访问上传的文件:${NC}"
echo -e "${YELLOW}${MINIO_ENDPOINT}/${BUCKET_NAME}/charts/文件名.html${NC}"

echo ""
echo -e "${GREEN}配置完成！可以使用以下命令测试:${NC}"
echo -e "${YELLOW}curl -I ${MINIO_ENDPOINT}/${BUCKET_NAME}/charts/test.html${NC}"

