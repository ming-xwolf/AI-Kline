# 缠论分析模块使用说明

## 概述

缠论分析模块是基于缠论理论开发的股票技术分析工具，能够自动识别股票走势中的笔、线段、中枢等关键结构，并提供相应的交易信号和投资建议。

## 核心功能

### 1. 笔识别 (Pen Recognition)
- **功能**: 自动识别价格走势中的笔
- **算法**: 基于分型点识别，确保笔的完整性和有效性
- **输出**: 笔的起始点、结束点、方向、长度等信息

### 2. 线段识别 (Segment Recognition)
- **功能**: 识别由笔组成的线段
- **算法**: 基于笔的方向一致性判断线段
- **输出**: 线段的起始笔、结束笔、方向、长度等信息

### 3. 中枢识别 (Zhongshu Recognition)
- **功能**: 识别价格震荡的中枢区域
- **算法**: 基于线段重叠判断中枢
- **输出**: 中枢的价格区间、中心价格、强度等信息

### 4. 趋势分析 (Trend Analysis)
- **功能**: 分析整体趋势方向和强度
- **算法**: 基于线段和中枢的综合分析
- **输出**: 趋势方向、强度、置信度等信息

### 5. 交易信号生成 (Trading Signals)
- **功能**: 基于缠论理论生成买卖信号
- **算法**: 识别突破、回调等关键信号
- **输出**: 信号类型、方向、强度、置信度等信息

## 模块结构

```
modules/
├── chan_analyzer.py          # 基础缠论分析器
├── chan_analysis_engine.py   # 高级缠论分析引擎
└── chan_visualizer.py        # 缠论可视化工具
```

## 使用方法

### 1. 基础使用

```python
from modules.chan_analyzer import ChanAnalyzer
from modules.data_fetcher import StockDataFetcher

# 获取股票数据
data_fetcher = StockDataFetcher()
stock_data = data_fetcher.fetch_stock_data("000001", "1年")

# 执行缠论分析
chan_analyzer = ChanAnalyzer()
analysis_result = chan_analyzer.analyze(stock_data)

# 查看结果
print(f"笔数量: {len(analysis_result['pen_data'])}")
print(f"线段数量: {len(analysis_result['segment_data'])}")
print(f"中枢数量: {len(analysis_result['zhongshu_data'])}")
```

### 2. 高级分析

```python
from modules.chan_analysis_engine import ChanAnalysisEngine

# 执行高级缠论分析
chan_engine = ChanAnalysisEngine()
advanced_analysis = chan_engine.advanced_chan_analysis(stock_data)

# 获取分析结果
analysis_result = advanced_analysis['analysis_result']
investment_advice = advanced_analysis['investment_advice']

print(f"综合评分: {analysis_result['overall_score']}")
print(f"投资建议: {investment_advice['action']}")
```

### 3. 可视化

```python
from modules.chan_visualizer import ChanVisualizer

# 创建可视化
visualizer = ChanVisualizer()

# 生成综合图表
chart_path = visualizer.create_comprehensive_chan_chart(
    stock_data, advanced_analysis, "output/chart.png"
)

# 生成分析报告
report = visualizer.create_chan_analysis_report(advanced_analysis, "000001")
```

## API 接口

### MCP 服务器接口

#### 1. 缠论分析
```bash
# 执行缠论分析
chan_analysis(symbol="000001", period="1年", frequency="daily")
```

#### 2. 生成缠论图表
```bash
# 生成缠论分析图表
chan_chart(symbol="000001", period="1年", frequency="daily")
```

### Web 接口

#### 1. 缠论分析接口
```http
POST /chan_analyze
Content-Type: application/x-www-form-urlencoded

stock_code=000001&period=1年
```

#### 2. 缠论图表接口
```http
POST /chan_chart
Content-Type: application/x-www-form-urlencoded

stock_code=000001&period=1年
```

## 分析结果说明

### 1. 笔分析结果
- **start_date**: 笔开始日期
- **end_date**: 笔结束日期
- **start_price**: 笔开始价格
- **end_price**: 笔结束价格
- **direction**: 笔方向 (up/down)
- **length**: 笔长度（天数）

### 2. 线段分析结果
- **start_pen**: 线段起始笔索引
- **end_pen**: 线段结束笔索引
- **direction**: 线段方向 (up/down)
- **length**: 线段长度（笔数）

### 3. 中枢分析结果
- **start_date**: 中枢开始日期
- **end_date**: 中枢结束日期
- **high**: 中枢上沿价格
- **low**: 中枢下沿价格
- **center**: 中枢中心价格
- **strength**: 中枢强度

### 4. 交易信号
- **type**: 信号类型 (breakout/pullback)
- **direction**: 信号方向 (up/down)
- **strength**: 信号强度 (strong/medium/weak)
- **confidence**: 信号置信度 (0-1)

### 5. 投资建议
- **action**: 操作建议 (buy/sell/hold)
- **confidence**: 建议置信度 (0-1)
- **target_price**: 目标价格
- **stop_loss**: 止损价格
- **time_horizon**: 时间周期 (short/medium/long)
- **risk_level**: 风险等级 (low/medium/high)

## 配置参数

### 分析配置
```python
analysis_config = {
    'min_pen_length': 3,           # 最小笔长度
    'min_segment_length': 2,        # 最小线段长度
    'zhongshu_min_segments': 3,     # 中枢最小线段数
    'trend_threshold': 0.6,        # 趋势判断阈值
    'signal_confidence_threshold': 0.5  # 信号置信度阈值
}
```

## 注意事项

1. **数据质量**: 确保股票数据完整，建议使用至少1年的日线数据
2. **参数调整**: 可根据不同市场环境调整分析参数
3. **风险提示**: 缠论分析仅供参考，不构成投资建议
4. **计算复杂度**: 高级分析需要较多计算资源，建议在性能较好的环境中运行

## 示例运行

```bash
# 运行缠论分析示例
conda activate AI-Kline && python chan_analysis_example.py
```

## 输出文件

- `{stock_code}_chan_analysis.png`: 缠论分析图表
- `{stock_code}_chan_analysis_report.txt`: 缠论分析报告
- `{stock_code}_chan_analysis_result.txt`: 详细分析结果

## 技术支持

如有问题或建议，请参考项目文档或联系开发团队。
