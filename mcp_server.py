from mcp.server.fastmcp import FastMCP

import os
import argparse
import json
import logging
import asyncio
from dotenv import load_dotenv

from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.visualizer import Visualizer
from modules.ai_analyzer import AIAnalyzer

# Initialize FastMCP server
mcp = FastMCP("AI-Kline", host=os.getenv("MCP_HOST", "0.0.0.0"), port=os.getenv("MCP_PORT", 8000))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

@mcp.tool()
async def ashare_analysis(symbol: str, period: str = '1年', frequency: str = 'daily'
                                   ) -> str:
    """
    分析股票
    Args:
        symbol: A股股票代码或者指数代码 (股票代码： 000001, 600001, 300001)
        period: 分析周期 (1年, 6个月, 3个月, 1个月, 1周)
        frequency: 数据频率 (daily-日线, weekly-周线, monthly-月线, 1min-1分钟, 5min-5分钟, 15min-15分钟, 30min-30分钟, 60min-60分钟)
    """
    try:
        analysis_result = await run_in_threadpool(pattern_run, symbol=symbol, period=period, frequency=frequency)
        return analysis_result
    except Exception as e:
        logger.error(f"Error analyzing stock pattern: {e}")
        return f"Failed to analyze stock pattern: {str(e)}"
    
@mcp.tool()
async def get_ashare_quote(symbol: str, period: str = '1周', frequency: str = 'daily'
                                   ) -> str:
    """
    获取股票行情数据
    Args:
        symbol: A股股票代码或者指数代码 (股票代码： 000001, 600001, 300001)
        period: 分析周期 (1年, 6个月, 3个月, 1个月, 1周)
        frequency: 数据频率 (daily-日线, weekly-周线, monthly-月线, 1min-1分钟, 5min-5分钟, 15min-15分钟, 30min-30分钟, 60min-60分钟)
    """
    try:
        data_fetcher = StockDataFetcher()
        stock_data = data_fetcher.fetch_stock_data(symbol, period, frequency)
        analysis_result = stock_data.to_dict()
        return str(analysis_result)
    except Exception as e:
        logger.error(f"Error analyzing stock pattern: {e}")
        return f"Failed to analyze stock pattern: {str(e)}"

@mcp.tool()
async def get_ashare_news(symbol: str
                                   ) -> str:
    """
    获取股票新闻
    Args:
        symbol: A股股票代码或者指数代码 (股票代码： 000001, 600001, 300001)
    """
    try:
        financial_data = {}
        data_fetcher = StockDataFetcher()
        news_data = data_fetcher.fetch_news_data(symbol)
        financial_data['news'] = news_data
        analysis_result = json.dumps(financial_data, ensure_ascii=False, indent=2)
        return analysis_result
    except Exception as e:
        logger.error(f"Error analyzing stock pattern: {e}")
        return f"Failed to analyze stock pattern: {str(e)}"
    
@mcp.tool()
async def get_ashare_financial(symbol: str
                                   ) -> str:
    """
    获取股票财务数据
    Args:
        symbol: A股股票代码或者指数代码 (股票代码： 000001, 600001, 300001)
    """
    try:
        data_fetcher = StockDataFetcher()
        financial_data = data_fetcher.fetch_financial_data(symbol)
        analysis_result = json.dumps(financial_data, ensure_ascii=False, indent=2)
        return analysis_result
    except Exception as e:
        logger.error(f"Error analyzing stock pattern: {e}")
        return f"Failed to analyze stock pattern: {str(e)}"

@mcp.tool()
async def get_ashare_echarts(symbol: str, period: str = '1年', indicators: str = 'MA,MACD,KDJ,BOLL,BIAS', frequency: str = 'daily') -> str:
    """
    获取股票K线图及技术指标的ECharts HTML
    Args:
        symbol: A股股票代码或者指数代码 (股票代码： 000001, 600001, 300001)
        period: 分析周期 (1年, 6个月, 3个月, 1个月, 1周)
        indicators: 技术指标列表，用逗号分隔 (MA,MACD,KDJ,BOLL,BIAS,RSI)
        frequency: 数据频率 (daily-日线, weekly-周线, monthly-月线, 1min-1分钟, 5min-5分钟, 15min-15分钟, 30min-30分钟, 60min-60分钟)
    """
    try:
        # 使用与ashare_analysis相同的保存路径
        save_path = './output'
        
        # 获取股票数据
        data_fetcher = StockDataFetcher()
        stock_data = data_fetcher.fetch_stock_data(symbol, period, frequency)
        
        if stock_data.empty:
            return "无法获取股票数据，请检查股票代码是否正确"
        
        # 计算技术指标
        technical_analyzer = TechnicalAnalyzer()
        indicators_data = technical_analyzer.calculate_indicators(stock_data)
        
        # 解析用户指定的指标
        requested_indicators = [ind.strip().upper() for ind in indicators.split(',')]
        
        # 生成ECharts HTML并保存
        visualizer = Visualizer()
        html_content = visualizer.create_echarts_html(
            stock_data, 
            indicators_data, 
            symbol, 
            requested_indicators,
            save_path,
            frequency
        )
        
        return f"ECharts HTML已生成并保存到output/charts目录\n\nHTML内容:\n{html_content}"
        
    except Exception as e:
        logger.error(f"Error generating ECharts HTML: {e}")
        return f"生成ECharts HTML失败: {str(e)}"
    

async def run_in_threadpool(func, *args, **kwargs):
    """Run a synchronous function in a threadpool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

def pattern_run(symbol: str, period: str = '1年', save_path: str = './output', frequency: str = 'daily') -> str:

    
    # 初始化各模块
    data_fetcher = StockDataFetcher()
    technical_analyzer = TechnicalAnalyzer()
    visualizer = Visualizer()
    ai_analyzer = AIAnalyzer()
    
    # 获取股票数据
    print(f"正在获取 {symbol} 的历史数据...")
    stock_data = data_fetcher.fetch_stock_data(symbol, period, frequency)
    
    # 获取财务和新闻数据
    print(f"正在获取 {symbol} 的财务和新闻数据...")
    financial_data = data_fetcher.fetch_financial_data(symbol)
    news_data = data_fetcher.fetch_news_data(symbol)
    
    # 计算技术指标
    print("正在计算技术指标...")
    indicators = technical_analyzer.calculate_indicators(stock_data)
    
    # 生成可视化图表
    print("正在生成K线图和技术指标图...")
    chart_path = visualizer.create_charts(stock_data, indicators, symbol, save_path, frequency)
    
    # AI分析预测
    print("正在使用AI分析预测未来走势...")
    analysis_result = ai_analyzer.analyze(stock_data, indicators, financial_data, news_data, symbol, save_path)

    return analysis_result 

if __name__ == "__main__":
    # mcp.run(transport='stdio')
    mcp.run(transport='streamable-http')
