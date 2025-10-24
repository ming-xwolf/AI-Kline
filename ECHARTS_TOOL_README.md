# AI-Kline ECharts 工具使用说明

## 新增功能

在AI-Kline模块的MCP服务中新增了 `get_ashare_echarts` 工具，用于生成包含技术指标的交互式ECharts HTML图表。

## 工具参数

### get_ashare_echarts

**功能**: 获取股票K线图及技术指标的ECharts HTML

**参数**:
- `symbol` (str): A股股票代码或者指数代码 (例如: 000001, 600001, 300001)
- `period` (str, 可选): 分析周期，默认为 '1年'
  - 可选值: '1年', '6个月', '3个月', '1个月', '1周'
- `indicators` (str, 可选): 技术指标列表，用逗号分隔，默认为 'MA,MACD,KDJ,BOLL,BIAS'
  - 支持的指标: MA, MACD, KDJ, BOLL, BIAS, RSI

## 使用示例

### 基本使用
```python
# 使用默认参数
result = await get_ashare_echarts("000001")

# 指定分析周期
result = await get_ashare_echarts("000001", period="6个月")

# 指定技术指标
result = await get_ashare_echarts("000001", indicators="MA,MACD,KDJ")
```

### 支持的股票代码
- 主板股票: 000001, 600001, 600036 等
- 创业板股票: 300001, 300002 等
- 科创板股票: 688001, 688002 等
- 指数代码: 000001 (上证指数), 399001 (深证成指) 等

## 技术指标说明

### MA (移动平均线)
- MA5: 5日移动平均线
- MA10: 10日移动平均线
- MA20: 20日移动平均线
- MA30: 30日移动平均线

### MACD (指数平滑移动平均线)
- MACD线: 快线
- Signal线: 信号线
- MACD柱: 柱状图

### KDJ (随机指标)
- K值: 快速随机值
- D值: 慢速随机值
- J值: 超买超卖指标

### BOLL (布林带)
- 上轨: 压力线
- 中轨: 中位线
- 下轨: 支撑线

### BIAS (乖离率)
- BIAS6: 6日乖离率
- BIAS12: 12日乖离率
- BIAS24: 24日乖离率

### RSI (相对强弱指标)
- RSI6: 6日RSI
- RSI12: 12日RSI
- RSI24: 24日RSI

## 返回结果

工具返回完整的HTML文档，包含：
- 交互式K线图
- 用户指定的技术指标图表
- 响应式设计，支持移动端查看
- 数据缩放和工具提示功能
- 图表导出功能

## 环境要求

确保在AI-Kline环境中运行：
```bash
conda activate AI-Kline && python mcp_server.py
```

## 注意事项

1. 首次使用需要安装依赖包
2. 股票数据获取需要网络连接
3. 生成的HTML文件较大，建议在浏览器中查看
4. 技术指标计算基于历史数据，需要足够的数据量

## 故障排除

### 常见问题

1. **无法获取股票数据**
   - 检查网络连接
   - 确认股票代码正确
   - 检查akshare库是否正常

2. **技术指标显示异常**
   - 确保数据量足够（建议至少60个交易日）
   - 检查数据质量

3. **HTML生成失败**
   - 检查pyecharts库是否正确安装
   - 确认Python版本兼容性

### 调试方法

```python
# 检查数据获取
data_fetcher = StockDataFetcher()
stock_data = data_fetcher.fetch_stock_data("000001", "1年")
print(f"数据量: {len(stock_data)}")

# 检查技术指标计算
technical_analyzer = TechnicalAnalyzer()
indicators = technical_analyzer.calculate_indicators(stock_data)
print(f"指标数量: {len(indicators)}")
```
