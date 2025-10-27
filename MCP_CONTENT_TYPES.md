# MCP 内容类型支持说明

## FastMCP 支持的 Content Types

根据 MCP (Model Context Protocol) 规范，FastMCP 支持以下内容类型：

### 标准内容类型

1. **TextContent** (`text/plain`)
   - 纯文本内容
   - 最常见的返回类型
   - 示例：返回分析结果、日志等

2. **ImageContent** (`image/*`)
   - 图片内容（base64 编码）
   - 支持：`image/png`, `image/jpeg`, `image/svg+xml`, `image/gif` 等
   - 示例：图表图片

3. **AudioContent** (`audio/*`)
   - 音频内容
   - 支持：`audio/mpeg`, `audio/wav`, `audio/ogg` 等

### ❓ 关于 HTML 内容

**FastMCP 并不直接支持 HTML 内容类型。**

但是可以通过以下方式处理 HTML：

#### 方案 1: 返回 HTML URL（推荐）

使用 MinIO 或其他对象存储，返回 HTML 的 URL：

```python
@mcp.tool()
async def get_ashare_echarts_html(symbol: str, ...) -> str:
    # 检查 MinIO 配置
    if not minio_storage_manager.is_configured():
        return json.dumps({
            "error": "MinIO not configured",
            "message": "请先配置 MinIO"
        })
    
    # 生成 HTML
    html_content = generate_echarts_html(...)
    
    # 上传到 MinIO
    url = minio_storage_manager.upload_html_sync(html_content, f"{symbol}_chart")
    
    # 返回 JSON 格式
    return json.dumps({"url": url})
```

**优点**：
- ✅ 返回简洁的 URL
- ✅ 减少响应数据大小
- ✅ 支持浏览器直接打开
- ✅ 可设置缓存策略

**当前实现**：✅ 已采用此方案

#### 方案 2: 返回 Base64 编码的 HTML

将 HTML 作为 base64 编码的字符串返回：

```python
import base64

@mcp.tool()
async def get_ashare_echarts(symbol: str, ...) -> str:
    html_content = generate_echarts_html(...)
    
    # Base64 编码
    html_base64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    return f"data:text/html;base64,{html_base64}"
```

**缺点**：
- ❌ 响应数据量大
- ❌ 不同客户端支持不一致

#### 方案 3: 将 HTML 转换为图片

使用 Selenium 将 HTML 渲染为图片，然后返回 ImageContent：

```python
@mcp.tool()
async def get_ashare_chart_image(symbol: str, ...):
    # 生成 ECharts HTML
    html_content = generate_echarts_html(...)
    
    # 使用 Selenium 渲染为图片
    image_base64 = render_html_to_image(html_content)
    
    # 返回 ImageContent
    return ImageContent(type="image", data=image_base64, mimeType="image/png")
```

**当前实现**：✅ `get_ashare_chart_image` 工具

### 📋 当前项目的内容类型使用

| 工具 | 返回类型 | 内容格式 | 说明 |
|------|----------|----------|------|
| `ashare_analysis` | TextContent | 文本分析报告 | ✅ 支持 |
| `get_ashare_quote` | TextContent | JSON 数据 | ✅ 支持 |
| `get_ashare_news` | TextContent | JSON 数据 | ✅ 支持 |
| `get_ashare_financial` | TextContent | JSON 数据 | ✅ 支持 |
| `get_ashare_echarts_html` | TextContent | JSON格式 MinIO URL | ✅ 支持 |
| `get_ashare_chart_image` | ImageContent | PNG/SVG 图片 | ✅ 支持 |
| `chan_analysis` | TextContent | 文本分析 | ✅ 支持 |
| `chan_chart` | TextContent | 图片路径 | ✅ 支持 |

### 💡 最佳实践

#### 对于 HTML 内容

1. **生成 HTML 图表并获取 URL** → 使用 `get_ashare_echarts_html`
   ```python
   # 当前实现 - 返回 JSON 格式
   result = await get_ashare_echarts_html("000001", "1年", "MA,MACD", "daily")
   # 返回: {"url": "http://localhost:9000/ai-kline-charts/charts/000001_chart_..."}
   ```
   **特性**：
   - ✅ 需要配置 MinIO
   - ✅ 返回 JSON 格式的 URL
   - ✅ 未配置 MinIO 时返回错误信息

2. **需要图片显示** → 使用 `get_ashare_chart_image`
   ```python
   # 返回 base64 图片
   result = await get_ashare_chart_image("000001")
   # 客户端可直接显示图片
   ```

#### 对于文本内容

直接返回字符串即可：

```python
@mcp.tool()
async def get_analysis(symbol: str) -> str:
    result = analyze_stock(symbol)
    return result  # FastMCP 自动处理为 TextContent
```

#### 对于图片内容

使用 ImageContent：

```python
@mcp.tool()
async def get_image():
    # 生成图片 base64
    image_data = generate_chart_base64(...)
    
    return {
        "type": "image",
        "data": image_data,
        "mimeType": "image/png"
    }
```

### 🔍 MCP Content Types 规范

根据 MCP 协议规范，标准内容类型定义如下：

```typescript
type Content = 
  | TextContent 
  | ImageContent 
  | EmbeddedResource
  | ReferencesResource

interface TextContent {
  type: "text"
  text: string
}

interface ImageContent {
  type: "image"
  data: string  // base64
  mimeType?: string
}
```

### 参考

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP SDK Python](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

