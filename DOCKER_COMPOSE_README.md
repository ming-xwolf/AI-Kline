# AI-Kline Docker Compose 使用指南

## 🐳 概述

AI-Kline 项目提供了完整的 Docker Compose 配置，支持一键部署包含 MCP 服务、MinIO 对象存储、Web 应用和 Nginx 反向代理的完整环境。

## 📋 服务组件

### 核心服务

| 服务 | 端口 | 描述 | 状态 |
|------|------|------|------|
| `ai-kline` | 20020 | MCP 服务 | 必需 |
| `minio` | 20021/20022 | 对象存储 | 必需 |

### 可选服务

| 服务 | 端口 | 描述 | Profile |
|------|------|------|---------|
| `ai-kline-web` | 20023 | Web 应用 | `web` |
| `nginx` | 20024/20025 | 反向代理 | `nginx` |

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd AI-Kline

# 创建环境配置文件
cp env.example .env

# 编辑配置文件
vim .env
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# AI 模型配置（必需）
AI_KLINE_API_KEY=your_api_key_here
AI_KLINE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_KLINE_MODEL_NAME=qwen-vl-max

# MinIO 配置（可选，默认使用容器内 MinIO）
MINIO_ENDPOINT=minio
MINIO_PORT=9000
MINIO_USE_SSL=false
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=ai-kline-charts
```

### 3. 启动服务

#### 基础服务（MCP + MinIO）

```bash
# 启动核心服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f ai-kline
```

#### 完整服务（包含 Web 应用）

```bash
# 启动所有服务
docker-compose --profile web up -d

# 查看所有服务
docker-compose ps
```

#### 生产环境（包含 Nginx）

```bash
# 启动生产环境（需要 SSL 证书）
docker-compose --profile web --profile nginx up -d
```

## 🔧 服务管理

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d ai-kline minio

# 启动带 profile 的服务
docker-compose --profile web up -d
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 停止特定服务
docker-compose stop ai-kline
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart ai-kline

# 重新构建并启动
docker-compose up -d --build
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f ai-kline
docker-compose logs -f minio

# 查看最近日志
docker-compose logs --tail=100 ai-kline
```

## 🌐 访问服务

### 服务端点

| 服务 | 访问地址 | 说明 |
|------|----------|------|
| MCP 服务 | http://localhost:20020 | MCP 协议端点 |
| MinIO API | http://localhost:20021 | 对象存储 API |
| MinIO 控制台 | http://localhost:20022 | Web 管理界面 |
| Web 应用 | http://localhost:20023 | AI-Kline Web 界面 |

### 通过 Nginx（如果启用）

| 服务 | 访问地址 | 说明 |
|------|----------|------|
| Web 应用 | https://localhost/ | 主 Web 界面 |
| MCP 服务 | https://localhost/mcp | MCP 协议端点 |
| MinIO API | https://localhost/minio/ | 对象存储 API |
| MinIO 控制台 | https://localhost/minio-console/ | Web 管理界面 |

### 默认凭证

- **MinIO 控制台**: `minioadmin` / `minioadmin`

## 📁 数据持久化

### 数据卷

- `minio-data`: MinIO 对象存储数据
- `./output`: AI-Kline 输出文件
- `./logs`: 应用日志文件

### 备份数据

```bash
# 备份 MinIO 数据
docker run --rm -v ai-kline_minio-data:/data -v $(pwd):/backup alpine tar czf /backup/minio-backup.tar.gz -C /data .

# 恢复 MinIO 数据
docker run --rm -v ai-kline_minio-data:/data -v $(pwd):/backup alpine tar xzf /backup/minio-backup.tar.gz -C /data
```

## 🔍 监控和调试

### 健康检查

```bash
# 检查服务健康状态
docker-compose ps

# 检查特定服务健康状态
docker inspect ai-kline-mcp | grep -A 10 Health
```

### 进入容器调试

```bash
# 进入 MCP 服务容器
docker-compose exec ai-kline bash

# 进入 MinIO 容器
docker-compose exec minio sh

# 查看容器资源使用
docker stats
```

### 查看服务日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f ai-kline
docker-compose logs -f minio

# 查看错误日志
docker-compose logs ai-kline | grep ERROR
```

## 🛠️ 开发模式

### 开发环境配置

```bash
# 使用开发环境配置
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 挂载源代码进行开发
docker-compose -f docker-compose.dev.yml up -d
```

### 调试模式

```bash
# 启动调试模式
DEBUG=true docker-compose up -d

# 查看详细日志
docker-compose logs -f ai-kline | grep DEBUG
```

## 🔒 SSL/TLS 配置

### 生成自签名证书

```bash
# 创建 SSL 目录
mkdir -p ssl

# 生成私钥
openssl genrsa -out ssl/key.pem 2048

# 生成证书
openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 -subj "/CN=localhost"
```

### 使用 Let's Encrypt

```bash
# 使用 certbot 生成证书
certbot certonly --standalone -d your-domain.com

# 复制证书到 ssl 目录
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

## 📊 性能优化

### 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  ai-kline:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 缓存优化

```bash
# 使用多阶段构建缓存
docker-compose build --parallel

# 清理未使用的镜像
docker system prune -a
```

## 🚨 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 检查服务状态
docker-compose ps

# 查看错误日志
docker-compose logs ai-kline

# 检查端口占用
netstat -tulpn | grep :20020
```

#### 2. MinIO 连接失败

```bash
# 检查 MinIO 状态
docker-compose logs minio

# 测试 MinIO 连接
curl http://localhost:20021/minio/health/live
```

#### 3. 权限问题

```bash
# 修复文件权限
sudo chown -R $USER:$USER output logs

# 检查容器权限
docker-compose exec ai-kline ls -la /app
```

### 重置环境

```bash
# 完全重置
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

## 📚 相关文档

- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [MinIO Docker 部署](https://docs.min.io/docs/deploy-minio-on-docker.html)
- [Nginx 配置指南](https://nginx.org/en/docs/)
- [AI-Kline 使用说明](./README.md)

## 💡 最佳实践

1. **生产环境**：使用 `--profile nginx` 启用反向代理
2. **数据备份**：定期备份 MinIO 数据卷
3. **监控**：配置健康检查和日志监控
4. **安全**：使用 HTTPS 和强密码
5. **资源**：根据负载调整容器资源限制

