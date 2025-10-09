# AI-Kline 启动脚本使用说明

本项目提供了多个便捷的启动脚本来管理 AI-Kline 服务。

## 脚本列表

### 1. 单独启动脚本

#### `start_mcp.sh` - 启动 MCP 服务
```bash
./start_mcp.sh
```
- 启动 AI-Kline MCP 服务（后台运行）
- 自动检查并创建 conda 环境
- 自动安装依赖包
- 设置必要的环境变量
- 日志保存到 `./logs/mcp_server_YYYYMMDD_HHMMSS.log`
- PID 保存到 `./logs/mcp_server.pid`

#### `start_web.sh` - 启动 Web 应用
```bash
./start_web.sh
```
- 启动 AI-Kline Web 应用（后台运行）
- 访问地址: http://localhost:5000
- 自动检查并创建 conda 环境
- 自动安装依赖包
- 日志保存到 `./logs/web_app_YYYYMMDD_HHMMSS.log`
- PID 保存到 `./logs/web_app.pid`

### 2. 完整服务脚本

#### `start_all.sh` - 同时启动所有服务
```bash
./start_all.sh
```
- 同时启动 MCP 服务和 Web 应用
- 在后台运行两个服务
- 按 Ctrl+C 可同时停止所有服务

### 3. 管理脚本

#### `stop_services.sh` - 停止所有服务
```bash
./stop_services.sh
```
- 停止所有运行中的 AI-Kline 相关服务
- 清理相关进程

#### `check_status.sh` - 检查服务状态
```bash
./check_status.sh
```
- 检查 conda 环境状态
- 检查服务运行状态（支持 PID 文件管理）
- 检查端口占用情况
- 检查环境变量设置
- 检查输出目录和日志目录
- 显示最新日志文件信息

#### `view_logs.sh` - 查看日志
```bash
./view_logs.sh [service] [lines]
```
- 查看指定服务的日志
- 支持参数：`web`、`mcp`、`all`
- 可指定显示行数（默认50行）
- 示例：
  - `./view_logs.sh web 100` - 查看 Web 应用最新100行日志
  - `./view_logs.sh mcp` - 查看 MCP 服务最新50行日志
  - `./view_logs.sh all` - 查看所有服务日志

## 使用步骤

### 首次使用

1. **设置环境变量**（必需）：
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **运行服务**：
   ```bash
   # 方式1: 启动所有服务
   ./start_all.sh
   
   # 方式2: 分别启动
   ./start_mcp.sh    # 终端1
   ./start_web.sh    # 终端2
   ```

3. **访问应用**：
   - Web 界面: http://localhost:5000
   - MCP 服务: 通过 MCP 客户端连接

### 日常使用

1. **检查状态**：
   ```bash
   ./check_status.sh
   ```

2. **查看日志**：
   ```bash
   # 查看所有服务日志
   ./view_logs.sh all
   
   # 查看 Web 应用日志
   ./view_logs.sh web 100
   
   # 实时查看日志
   tail -f ./logs/web_app_20241201_143022.log
   ```

3. **停止服务**：
   ```bash
   ./stop_services.sh
   ```

## 环境要求

- macOS/Linux 系统
- conda 已安装
- Python 3.11

## 故障排除

### 1. 权限问题
如果脚本无法执行，请确保脚本有执行权限：
```bash
chmod +x *.sh
```

### 2. conda 环境问题
如果 conda 命令不可用，请初始化 conda：
```bash
conda init zsh
exec zsh
```

### 3. 端口占用
如果端口 5000 被占用，可以修改 `web_app.py` 中的端口号。

### 4. 依赖安装失败
如果依赖安装失败，可以手动安装：
```bash
conda activate AI-Kline
pip install -r requirements.txt
```

### 5. matplotlib 错误
如果遇到 matplotlib GUI 相关错误，脚本已自动设置 `MPLBACKEND=Agg`，这应该能解决问题。

## 注意事项

- 首次运行会自动创建 conda 环境并安装依赖
- 确保在项目根目录下运行脚本
- 建议在运行前先设置 `OPENAI_API_KEY` 环境变量
- 服务现在在后台运行，使用 `./stop_services.sh` 停止服务
- 日志文件按时间戳命名，便于追踪问题
- PID 文件用于进程管理，避免重复启动
- 使用 `./view_logs.sh` 方便查看日志内容

## 日志管理

### 日志文件位置
- Web 应用日志: `./logs/web_app_YYYYMMDD_HHMMSS.log`
- MCP 服务日志: `./logs/mcp_server_YYYYMMDD_HHMMSS.log`
- PID 文件: `./logs/web_app.pid`、`./logs/mcp_server.pid`

### 常用日志操作
```bash
# 查看最新日志
./view_logs.sh all

# 实时监控日志
tail -f ./logs/web_app_20241201_143022.log

# 搜索错误信息
grep -i error ./logs/*.log

# 清理旧日志（保留最近7天）
find ./logs -name "*.log" -mtime +7 -delete
```
