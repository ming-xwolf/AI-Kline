# MinIO 快速启动指南

AI-Kline 集成了 MinIO 对象存储，用于存储生成的 HTML 图表并提供 URL 访问。

## 🚀 快速开始

### 1. 安装 MinIO

#### macOS (推荐)
```bash
brew install minio/stable/minio
```

#### Linux
```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/
```

#### Docker (备选方案)
```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v ~/minio-data:/data \
  minio/minio server /data --console-address :9001
```

### 2. 启动 MinIO

```bash
# 启动 MinIO 服务
./start_minio.sh
```

**服务信息：**
- API 端点: http://localhost:9000
- 控制台: http://localhost:9001
- 默认凭证: `minioadmin` / `minioadmin`

### 3. 配置环境变量

创建或编辑 `.env` 文件：

```bash
cp env.example .env
```

添加 MinIO 配置：

```bash
# MinIO 对象存储配置
MINIO_ENDPOINT=localhost
MINIO_PORT=9000
MINIO_USE_SSL=false
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=ai-kline-charts
```

### 4. 使用 AI-Kline 工具

现在 `get_ashare_echarts` 工具会自动将 HTML 图表存储到 MinIO 并返回 URL：

```python
# 使用 get_ashare_echarts 工具
result = await get_ashare_echarts("000001", "1年", "MA,MACD", "daily")

# 输出：
# "图表已生成并存储在 MinIO，访问 URL: http://localhost:9000/ai-kline-charts/charts/000001_chart_20240101_120000.html"
```

## 📋 常用命令

### 启动/停止 MinIO

```bash
# 启动 MinIO
./start_minio.sh

# 停止 MinIO
./stop_minio.sh

# 检查 MinIO 状态
./check_minio.sh
```

### 查看日志

```bash
# 查看 MinIO 日志
tail -f ./logs/minio_*.log

# 或使用日志查看脚本
./view_logs.sh all
```

## 🌐 访问 MinIO

### Web 控制台

打开浏览器访问：http://localhost:9001

**登录信息：**
- 用户名: `minioadmin`
- 密码: `minioadmin`

在控制台中可以：
- 查看存储桶和文件
- 管理访问策略
- 监控存储使用情况
- 配置 CORS 规则

### API 端点

使用 MinIO 客户端工具或 SDK 连接到：

```
http://localhost:9000
```

## 🛠️ 管理存储桶

### 使用 MinIO 客户端 (mc)

#### 安装 mc

```bash
# macOS
brew install minio/stable/mc

# Linux
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/
```

#### 配置别名

```bash
mc alias set myminio http://localhost:9000 minioadmin minioadmin
```

#### 管理存储桶

```bash
# 列出所有存储桶
mc ls myminio

# 创建存储桶（通常自动创建）
mc mb myminio/ai-kline-charts

# 查看存储桶内容
mc ls myminio/ai-kline-charts

# 设置公开访问（如果需要）
mc anonymous set download myminio/ai-kline-charts
```

## 🔧 故障排除

### 问题 1: MinIO 启动失败

**错误**: 端口已被占用

**解决方案**:
```bash
# 检查端口占用
lsof -i :9000
lsof -i :9001

# 停止占用端口的进程
./stop_minio.sh
```

### 问题 2: 无法连接 MinIO

**检查清单**:
1. MinIO 服务是否运行: `./check_minio.sh`
2. 环境变量是否正确: `cat .env | grep MINIO`
3. 防火墙是否阻止: `telnet localhost 9000`

### 问题 3: 上传失败

**日志检查**:
```bash
tail -f ./logs/minio_*.log
```

**常见原因**:
- MinIO 未配置或未启动
- 网络连接问题
- 权限配置错误

## 📊 监控和统计

### 查看存储使用

```bash
# 使用 MinIO 客户端
mc du myminio

# 查看特定存储桶
mc du myminio/ai-kline-charts
```

### 查看文件列表

```bash
# 列出所有文件
mc ls myminio/ai-kline-charts/charts/

# 递归列出
mc ls -r myminio/ai-kline-charts/
```

### 清理旧文件

```bash
# 删除7天前的文件
mc rm --recursive --older-than 7d myminio/ai-kline-charts/charts/

# 手动删除特定文件
mc rm myminio/ai-kline-charts/charts/old_file.html
```

## 🔒 安全建议

### 1. 更改默认密码

**MinIO 控制台**:
1. 访问 http://localhost:9001
2. 登录后进入 Settings → Identity → Service Accounts
3. 修改 Access Key 和 Secret Key

**更新 .env**:
```bash
MINIO_ACCESS_KEY=your_new_access_key
MINIO_SECRET_KEY=your_new_secret_key
```

### 2. 启用 SSL/TLS

在生产环境中，建议启用 SSL：

```bash
# 启动时使用 SSL
minio server ~/minio-data \
  --address :9000 \
  --console-address :9001 \
  --certs-dir ~/minio-certs
```

更新配置：
```bash
MINIO_USE_SSL=true
MINIO_ENDPOINT=your-domain.com
```

### 3. 配置 CORS（如果需要跨域访问）

```bash
mc cors set allow myminio/ai-kline-charts
```

## 📚 相关文档

- [MinIO 官方文档](https://min.io/docs/)
- [Python MinIO 客户端](https://github.com/minio/minio-py)
- [MinIO 集成说明](./MINIO_INTEGRATION.md)
- [脚本使用说明](./SCRIPTS_README.md)

## 💡 提示

1. **可选特性**: MinIO 集成是可选的，未配置时工具仍然正常工作
2. **性能优势**: 使用 MinIO URL 比嵌入 Base64 数据性能更好
3. **数据持久化**: MinIO 数据存储在 `~/minio-data` 目录
4. **备份数据**: 定期备份 `~/minio-data` 目录以避免数据丢失
5. **资源监控**: 注意监控磁盘空间使用情况

