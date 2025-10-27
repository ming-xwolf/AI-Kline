# MinIO 集成说明

AI-Kline 模块已集成 MinIO 对象存储功能，可以将生成的 HTML 图表存储在 MinIO 中并返回 URL，实现更好的性能和分享能力。

## 功能特性

- ✅ HTML 图表存储在 MinIO 对象存储中
- ✅ 自动返回可访问的 URL
- ✅ 如果 MinIO 未配置或不可用，自动回退到返回 HTML 内容
- ✅ 参考 mcp-echarts 模块的实现，保持一致性

## 配置 MinIO

### 环境变量

在 `.env` 文件中配置以下环境变量：

```bash
# MinIO 对象存储配置（可选）
MINIO_ENDPOINT=localhost          # MinIO 服务器地址
MINIO_PORT=9000                   # MinIO 服务器端口
MINIO_USE_SSL=false               # 是否使用 SSL
MINIO_ACCESS_KEY=minioadmin       # 访问密钥
MINIO_SECRET_KEY=minioadmin       # 密钥
MINIO_BUCKET_NAME=ai-kline-charts # 存储桶名称
```

### 安装 MinIO

#### macOS

```bash
# 使用 Homebrew 安装
brew install minio/stable/minio

# 启动 MinIO 服务器（数据目录 ~/minio-data，管理控制台 :9001）
minio server ~/minio-data --console-address :9001
```

#### Linux

```bash
# 下载 MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio

# 启动 MinIO 服务器
./minio server ~/minio-data --console-address :9001
```

#### Docker

```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v ~/minio-data:/data \
  minio/minio server /data --console-address :9001
```

### 访问 MinIO

- **API 端点**: http://localhost:9000 (本地模式) 或 http://localhost:20021 (Docker 模式)
- **管理控制台**: http://localhost:9001 (本地模式) 或 http://localhost:20022 (Docker 模式)
- **默认凭据**: 
  - Access Key: `minioadmin`
  - Secret Key: `minioadmin`
  
**注意**: Docker 模式下端口映射为 `20021:9000` 和 `20022:9001`，因此在 Docker 模式下访问 MinIO 需要使用映射后的端口。

### 配置公共访问权限

默认情况下，MinIO 存储桶是私有的。需要设置公共访问权限才能通过 URL 访问上传的 HTML 文件。

#### 自动配置脚本

项目提供了自动配置脚本，支持灵活的 IP 和端口配置：

```bash
# 使用默认值（localhost:9000）
./configure_minio_access.sh

# 指定 IP 和端口（推荐）
./configure_minio_access.sh localhost 9000    # 本地模式
./configure_minio_access.sh localhost 20021   # Docker 模式

# 使用环境变量
export MINIO_HOST=localhost
export MINIO_PORT=20021
./configure_minio_access.sh

# 远程服务器
./configure_minio_access.sh minio.example.com 9000
```

**参数说明**:
- 第一个参数: MinIO 主机地址（默认: localhost）
- 第二个参数: MinIO 端口（默认: 9000）
- 第三个参数: 存储桶名称（默认: ai-kline-charts）

脚本会自动安装 `mc` 客户端（如果未安装），配置别名，创建存储桶并设置公共访问权限。

#### 手动配置

如果脚本无法运行，可以手动配置：

```bash
# 1. 安装 mc 客户端（macOS）
brew install minio/stable/mc

# 2. 配置 MinIO 别名
mc alias set ai-kline-local http://localhost:9000 minioadmin minioadmin

# 3. 确保存储桶存在
mc mb ai-kline-local/ai-kline-charts

# 4. 设置公共下载权限
mc anonymous set download ai-kline-local/ai-kline-charts/

# 5. 验证配置
mc anonymous get ai-kline-local/ai-kline-charts
# 应该输出: Access permission for `ai-kline-local/ai-kline-charts/` is `download`
```

#### 在 Docker 中配置

如果使用 Docker 运行 MinIO：

```bash
# 进入 MinIO 容器
docker exec -it ai-kline-minio sh

# 安装 mc（在容器内）
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# 配置和设置权限
./mc alias set local http://localhost:9000 minioadmin minioadmin
./mc anonymous set download local/ai-kline-charts/
./mc anonymous get local/ai-kline-charts
```

## 使用方法

### 1. 安装依赖

```bash
conda activate AI-Kline && pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件，配置 MinIO 参数
```

### 3. 使用工具

#### 使用 get_ashare_echarts_html 工具

```python
# 需要先配置 MinIO 并设置公共访问权限
# 生成图表，返回 JSON 格式的 URL
result = await get_ashare_echarts_html("000001", "1年", "MA,MACD", "daily")

# 成功时返回:
# {"url": "http://localhost:9000/ai-kline-charts/charts/000001_chart_20240101_120000.html"}

# MinIO 未配置时返回:
# {"error": "MinIO not configured", "message": "请先配置 MinIO"}
```

#### 解析返回结果

```python
import json

result = await get_ashare_echarts_html("000001", "1年", "MA,MACD", "daily")
data = json.loads(result)

if "url" in data:
    print(f"图表 URL: {data['url']}")
    # 可以在浏览器中打开该 URL
elif "error" in data:
    print(f"错误: {data['error']}")
    print(f"信息: {data.get('message', '')}")
```

## 代码实现

### 新增文件

- `AI-Kline/modules/minio_storage.py` - MinIO 集成模块

### 修改文件

- `AI-Kline/mcp_server.py` - 更新 `get_ashare_echarts` 工具
- `AI-Kline/requirements.txt` - 添加 `minio>=7.2.0` 依赖
- `AI-Kline/env.example` - 添加 MinIO 配置示例

### 核心实现

```python
# 模块导入
from modules.minio_storage import store_html_to_minio, is_minio_configured

# echarts_run 函数增强
def echarts_run(symbol: str, period: str = '1年', ..., use_minio: bool = True) -> str:
    html_content = visualizer.create_echarts_html(...)
    
    # 如果启用了 MinIO 且已配置，上传到 MinIO
    if use_minio and is_minio_configured():
        url = store_html_to_minio(html_content, f"{symbol}_chart")
        if url:
            return f"图表已生成并存储在 MinIO，访问 URL: {url}"
    
    # 回退到 HTML 内容
    return f"```html\n{html_content}\n```"
```

## 工作原理

1. **检查配置**:** 使用 `is_minio_configured()` 检查是否已配置 MinIO
2. **上传文件**:** 调用 `store_html_to_minio()` 上传 HTML 内容到 MinIO
3. **生成 URL**:** 返回可访问的 URL
4. **自动回退**:** 如果 MinIO 不可用，返回原始 HTML 内容

## 与 mcp-echarts 的对比

| 特性 | mcp-echarts | AI-Kline |
|------|-------------|----------|
| 存储内容 | PNG/SVG 图片 | HTML 图表 |
| 客户端库 | `minio` (Node.js) | `minio` (Python) |
| 检查函数 | `isMinIOConfigured()` | `is_minio_configured()` |
| 存储函数 | `storeBufferToMinIO()` | `store_html_to_minio()` |
| URL 格式 | `${protocol}://${endpoint}:${port}/${bucket}/${object}` | 相同 |
| 回退机制 | Base64 图片数据 | HTML 文本内容 |

## 故障排除

### 问题 1: 无法连接到 MinIO

**错误信息**: `MinIO 存储失败，回退到本地` 或返回 `{"error": "upload failed"}`

**解决方案**:
- 检查 MinIO 服务器是否正在运行
  ```bash
  # 检查 MinIO 是否运行
  ./check_minio.sh
  
  # 或手动检查
  curl http://localhost:9000/minio/health/live
  ```
- 验证 `MINIO_ENDPOINT` 和 `MINIO_PORT` 配置是否正确
- 检查防火墙设置

### 问题 2: 认证失败

**错误信息**: `Authentication failed`

**解决方案**:
- 验证 `MINIO_ACCESS_KEY` 和 `MINIO_SECRET_KEY` 是否正确
- 检查 MinIO 服务器的凭据设置

### 问题 3: Bucket 不存在

**自动处理**: 如果 bucket 不存在，系统会自动创建

**手动创建**:
```bash
mc alias set myminio http://localhost:9000 minioadmin minioadmin
mc mb myminio/ai-kline-charts
```

### 问题 4: Access Denied (403) - 文件无法访问

**错误信息**: 访问 URL 返回 403 错误

**解决方案**:
- 设置存储桶的公共访问权限
  ```bash
  # 使用提供的脚本（推荐）
  ./configure_minio_access.sh localhost 20021  # Docker 模式
  ./configure_minio_access.sh localhost 9000   # 本地模式
  
  # 或手动设置
  mc alias set ai-kline-local http://localhost:20021 minioadmin minioadmin
  mc anonymous set download ai-kline-local/ai-kline-charts/
  mc anonymous get ai-kline-local/ai-kline-charts
  ```

### 问题 5: MinIO 未配置错误

**错误信息**: `{"error": "MinIO not configured", "message": "请先配置 MinIO"}`

**解决方案**:
- 检查 `.env` 文件中是否配置了以下变量：
  ```bash
  # 本地模式配置
  MINIO_ENDPOINT=localhost
  MINIO_PORT=9000
  MINIO_ACCESS_KEY=minioadmin
  MINIO_SECRET_KEY=minioadmin
  MINIO_BUCKET_NAME=ai-kline-charts
  
  # Docker 模式配置（需要设置外部访问地址）
  MINIO_ENDPOINT=minio
  MINIO_PORT=9000
  MINIO_EXTERNAL_ENDPOINT=localhost
  MINIO_EXTERNAL_PORT=20021
  ```
- 确保变量名称正确，区分大小写
- Docker 模式下必须设置 `MINIO_EXTERNAL_ENDPOINT` 和 `MINIO_EXTERNAL_PORT`

## 监控和日志

系统会记录以下日志：

- `INFO`: HTML 图表已上传到 MinIO
- `WARNING`: MinIO 上传失败，返回 HTML 内容
- `ERROR`: 生成图表失败

查看日志：

```bash
conda activate AI-Kline && tail -f logs/mcp_server_*.log
```

## 参考文档

- [MinIO 官方文档](https://min.io/docs/)
- [Python MinIO 客户端](https://github.com/minio/minio-py)
- [mcp-echarts MinIO 集成](https://github.com/hustcc/mcp-echarts)

## 注意事项

1. **可选特性**: MinIO 集成是可选的，如果未配置，工具仍然正常工作
2. **安全性**: 确保 MinIO 访问凭据安全存储，不要提交到版本控制
3. **性能**: 使用 MinIO URL 比 Base64 嵌入数据性能更好
4. **存储成本**: 考虑 MinIO 存储空间使用情况，定期清理旧文件

