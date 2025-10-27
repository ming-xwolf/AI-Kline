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
from modules.chan_analyzer import ChanAnalyzer
from modules.chan_analysis_engine import ChanAnalysisEngine
from modules.chan_visualizer import ChanVisualizer
from modules.image_generator import ImageGenerator
from modules.minio_storage import minio_storage_manager, is_minio_configured

# 尝试导入 MCP ImageContent 类型
try:
    from mcp.types import ImageContent
    MCP_IMAGE_AVAILABLE = True
except ImportError:
    try:
        from mcp.server.models import ImageContent
        MCP_IMAGE_AVAILABLE = True
    except ImportError:
        MCP_IMAGE_AVAILABLE = False
        ImageContent = None

# Initialize FastMCP server
mcp = FastMCP("AI-Kline", host=os.getenv("MCP_HOST", "0.0.0.0"), port=os.getenv("MCP_PORT", 8000))

# AI-Kline MCP服务器工具说明
"""
AI-Kline MCP服务器提供专业的A股股票分析工具集

主要功能模块:
1. 股票数据分析 (ashare_analysis) - 全面的技术分析和AI智能分析
2. 行情数据获取 (get_ashare_quote) - 获取股票历史行情数据
3. 新闻资讯获取 (get_ashare_news) - 获取股票相关新闻和公告
4. 财务数据获取 (get_ashare_financial) - 获取公司财务指标和基本面数据
5. K线图HTML生成 (generate_candlestick_html_chart) - 生成交互式K线图并上传到MinIO
6. K线图图片生成 (generate_candlestick_image_chart) - 生成PNG/SVG格式的K线图图片
7. 缠论技术分析 (chan_analysis) - 基于缠论理论的走势分析
8. 缠论图表生成 (chan_chart) - 生成缠论分析可视化图表

支持的股票类型:
- 主板股票 (000001, 600036等)
- 创业板股票 (300001等)
- 科创板股票 (688001等)
- 指数代码 (000001上证指数, 399001深证成指等)

支持的时间周期:
- 1年, 6个月, 3个月, 1个月, 1周

支持的数据频率:
- 日线 (daily), 周线 (weekly), 月线 (monthly)
- 分钟线: 1min, 5min, 15min, 30min, 60min

技术指标支持:
- MA (移动平均线)
- MACD (MACD指标)
- KDJ (KDJ随机指标)
- BOLL (布林带)

使用建议:
- 对于长期投资分析，推荐使用日线或周线数据
- 对于短期交易分析，推荐使用分钟线数据
- 缠论分析建议使用日线数据以获得最佳效果
- 技术指标可根据需要自由组合使用
"""

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# @mcp.tool()
async def ashare_analysis(symbol: str, period: str = '1年', frequency: str = 'daily'
                                   ) -> str:
    """
    执行A股股票的全面技术分析，包括K线图、技术指标计算、AI智能分析和投资建议
    
    功能特性:
    - 获取股票历史数据（支持多种时间周期和频率）
    - 计算多种技术指标（MA、MACD、KDJ、BOLL、RSI等）
    - 生成专业的K线图和技术指标图表
    - 使用AI分析股票走势并给出投资建议
    - 获取财务数据和新闻资讯进行综合分析
    
    参数说明:
        symbol (str): A股股票代码，支持以下格式：
            - 主板股票：000001（平安银行）、600036（招商银行）
            - 创业板股票：300001（特锐德）
            - 科创板股票：688001（华兴源创）
            - 指数代码：000001（上证指数）、399001（深证成指）
        period (str): 分析周期，可选值：
            - '1年'：获取1年历史数据（默认）
            - '6个月'：获取6个月历史数据
            - '3个月'：获取3个月历史数据
            - '1个月'：获取1个月历史数据
            - '1周'：获取1周历史数据
        frequency (str): 数据频率，可选值：
            - 'daily'：日线数据（默认）
            - 'weekly'：周线数据
            - 'monthly'：月线数据
            - '1min'：1分钟K线
            - '5min'：5分钟K线
            - '15min'：15分钟K线
            - '30min'：30分钟K线
            - '60min'：60分钟K线
    
    返回值:
        str: 包含以下内容的分析报告：
            - 股票基本信息
            - 技术指标分析结果
            - AI智能分析结论
            - 投资建议和风险提示
            - 图表文件保存路径
    
    使用示例:
        # 分析平安银行1年日线数据
        result = await ashare_analysis("000001", "1年", "daily")
        
        # 分析招商银行6个月周线数据
        result = await ashare_analysis("600036", "6个月", "weekly")
        
        # 分析创业板股票1个月5分钟数据
        result = await ashare_analysis("300001", "1个月", "5min")
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
    获取A股股票的实时行情和历史数据
    
    功能特性:
    - 获取股票的开盘价、收盘价、最高价、最低价
    - 获取成交量、成交额等交易数据
    - 支持多种时间周期和频率的数据获取
    - 返回结构化的股票数据，便于进一步分析
    
    参数说明:
        symbol (str): A股股票代码，支持主板、创业板、科创板股票
        period (str): 数据周期，默认'1周'，可选：
            - '1年'、'6个月'、'3个月'、'1个月'、'1周'
        frequency (str): 数据频率，默认'daily'，可选：
            - 'daily'、'weekly'、'monthly'、'1min'、'5min'、'15min'、'30min'、'60min'
    
    返回值:
        str: JSON格式的股票数据，包含：
            - 时间序列数据
            - OHLCV数据（开高低收量）
            - 技术指标基础数据
    
    使用示例:
        # 获取平安银行1周日线数据
        data = await get_ashare_quote("000001", "1周", "daily")
        
        # 获取招商银行1个月5分钟数据
        data = await get_ashare_quote("600036", "1个月", "5min")
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
    获取A股股票相关的新闻资讯和公告信息
    
    功能特性:
    - 获取股票相关的财经新闻
    - 获取公司公告和重大事项
    - 获取行业动态和市场资讯
    - 提供新闻时间、来源和内容摘要
    
    参数说明:
        symbol (str): A股股票代码，支持：
            - 主板股票：000001、600036等
            - 创业板股票：300001等
            - 科创板股票：688001等
    
    返回值:
        str: JSON格式的新闻数据，包含：
            - 新闻标题和内容
            - 发布时间和来源
            - 新闻分类和重要性
            - 相关股票代码
    
    使用示例:
        # 获取平安银行相关新闻
        news = await get_ashare_news("000001")
        
        # 获取招商银行相关新闻
        news = await get_ashare_news("600036")
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
    获取A股股票的财务数据和基本面信息
    
    功能特性:
    - 获取公司财务报表数据（资产负债表、利润表、现金流量表）
    - 获取关键财务指标（PE、PB、ROE、ROA等）
    - 获取公司基本信息（市值、股本、行业分类等）
    - 提供财务数据的趋势分析
    
    参数说明:
        symbol (str): A股股票代码，支持：
            - 主板股票：000001、600036等
            - 创业板股票：300001等
            - 科创板股票：688001等
    
    返回值:
        str: JSON格式的财务数据，包含：
            - 基本财务指标
            - 盈利能力指标
            - 偿债能力指标
            - 运营能力指标
            - 成长能力指标
    
    使用示例:
        # 获取平安银行财务数据
        financial = await get_ashare_financial("000001")
        
        # 获取招商银行财务数据
        financial = await get_ashare_financial("600036")
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
async def generate_candlestick_html_chart(symbol: str, period: str = '1年', indicators: str = 'MA,MACD,KDJ,BOLL,BIAS', frequency: str = 'daily') -> str:
    """
    生成K线图HTML图表
    
    功能特性:
    - 生成A股股票的HTML ECharts K线图表
    - 支持多种技术指标叠加显示（MA, MACD, KDJ, RSI, BOLL, BIAS等）
    - 将HTML文件上传到MinIO对象存储并返回可访问的URL
    - 交互式图表，支持缩放、数据提示等
    - 需要配置MinIO，否则会返回错误提示
    
    适用场景:
    - 生成交互式金融数据可视化图表
    - 在Web应用中嵌入金融K线图
    - 分享和保存金融分析图表
    
    参数说明:
        symbol (str): A股股票代码，支持主板、创业板、科创板股票
        period (str): 分析周期，默认'1年'，可选：
            - '1年'、'6个月'、'3个月'、'1个月'、'1周'
        indicators (str): 技术指标列表，用逗号分隔，默认'MA,MACD,KDJ,BOLL,BIAS'，可选：
            - 'MA'：移动平均线
            - 'MACD'：MACD指标
            - 'KDJ'：KDJ随机指标
            - 'BOLL'：布林带
            - 'BIAS'：乖离率
            - 'RSI'：相对强弱指标
        frequency (str): 数据频率，默认'daily'，可选：
            - 'daily'、'weekly'、'monthly'、'1min'、'5min'、'15min'、'30min'、'60min'
    
    返回值:
        str: JSON格式字符串 {"url": "MinIO_URL"}
        
    使用示例:
        # 生成平安银行1年日线K线图
        result = await generate_candlestick_html_chart("000001", "1年", "MA,MACD", "daily")
        
        # 生成招商银行6个月周线K线图
        result = await generate_candlestick_html_chart("600036", "6个月", "MA,MACD,KDJ,BOLL,RSI", "weekly")
        
        # 解析返回的JSON
        import json
        data = json.loads(result)
        if "url" in data:
            print(f"图表URL: {data['url']}")
    """
    try:
        # 检查 MinIO 配置
        if not minio_storage_manager.is_configured():
            return json.dumps({
                "error": "MinIO not configured",
                "message": "请先配置 MinIO"
            }, ensure_ascii=False)
        
        # 使用 use_minio=True 强制上传到 MinIO
        result = await run_in_threadpool(echarts_run, symbol=symbol, period=period, indicators=indicators, frequency=frequency, use_minio=True)
        
        # 解析结果
        try:
            data = json.loads(result)
            if "url" in data:
                return result  # 返回 JSON 格式
            else:
                return json.dumps({
                    "error": "upload failed",
                    "message": "MinIO upload failed, returned HTML content instead"
                }, ensure_ascii=False)
        except json.JSONDecodeError:
            # 如果返回的是 HTML 内容而不是 JSON，说明上传失败
            return json.dumps({
                "error": "upload failed",
                "message": "MinIO upload failed, please check configuration"
            }, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"Error generating ECharts HTML URL: {e}")
        return json.dumps({
            "error": "generation failed",
            "message": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def generate_candlestick_image_chart(symbol: str, period: str = '1年', indicators: str = 'MA,MACD,KDJ,BOLL', frequency: str = 'daily', width: int = 800, height: int = 600, output_type: str = 'png', upload_to_minio: bool = True) -> str:
    """
    生成K线图图片格式图表
    
    功能特性:
    - 生成A股股票的PNG/SVG图片格式K线图表
    - 支持多种技术指标叠加显示（MA, MACD, KDJ, RSI, BOLL, BIAS等）
    - 图片以Base64格式返回，可直接在聊天界面显示
    - 如果启用 MinIO 上传，将图片上传到 MinIO 并返回 URL
    - 支持自定义图片尺寸和质量
    - 自动保存图片到本地 output/charts 目录
    
    适用场景:
    - 需要直接在聊天界面显示图表（Base64）
    - 需要分享和访问图片（MinIO URL）
    - 生成报告和文档中的图表
    - 移动端和离线查看图表
    - 自定义图表尺寸和格式

    参数说明:
        symbol (str): A股股票代码，支持主板、创业板、科创板股票
        period (str): 分析周期，默认'1年'，可选：
            - '1年'、'6个月'、'3个月'、'1个月'、'1周'
        indicators (str): 技术指标列表，用逗号分隔，默认'MA,MACD,KDJ,BOLL'，可选：
            - 'MA'：移动平均线
            - 'MACD'：MACD指标
            - 'KDJ'：KDJ随机指标
            - 'BOLL'：布林带
        frequency (str): 数据频率，默认'daily'，可选：
            - 'daily'、'weekly'、'monthly'、'1min'、'5min'、'15min'、'30min'、'60min'
        width (int): 图片宽度，默认800像素
        height (int): 图片高度，默认600像素（自动根据子图数量调整）
        output_type (str): 输出格式，默认'png'，可选：
            - 'png'：PNG图片格式
            - 'svg'：SVG矢量图格式
        upload_to_minio (bool): 是否上传到MinIO，默认True
    
    返回值:
        如果 upload_to_minio=True 且 MinIO 已配置:
            str: JSON格式字符串 {"url": "MinIO_URL"}
        否则:
            ImageContent: MCP ImageContent对象，包含base64编码的图片数据
                - type: "image"
                - data: base64编码的图片数据
                - mimeType: 图片MIME类型（image/png 或 image/svg+xml）

    
    使用示例:
        # 生成平安银行1年日线PNG图表，包含MA和MACD指标
        result = await generate_candlestick_image_chart("000001", "1年", "MA,MACD", "daily", 800, 600, "png")
        
        # 生成招商银行6个月周线SVG图表，包含所有技术指标
        result = await generate_candlestick_image_chart("600036", "6个月", "MA,MACD,KDJ,BOLL", "weekly", 1000, 700, "svg")
        
        # 生成创业板股票1个月5分钟PNG图表
        result = await generate_candlestick_image_chart("300001", "1个月", "MA,MACD", "5min", 1200, 800, "png")
    """
    try:
        # chart_image_run 返回：
        # - PNG: base64 字符串
        # - SVG: SVG 字符串（未编码）
        chart_data = await run_in_threadpool(chart_image_run, symbol=symbol, period=period, indicators=indicators, frequency=frequency, width=width, height=height, output_type=output_type)
        
        # 根据输出类型确定 mimeType 和最终数据
        if output_type == "svg":
            # SVG: 将字符串转换为 base64
            import base64
            mime_type = "image/svg+xml"
            base64_data = base64.b64encode(chart_data.encode('utf-8')).decode('utf-8')
        else:
            # PNG: 已经是 base64
            mime_type = "image/png"
            base64_data = chart_data
        
        # 如果启用了 MinIO 上传且已配置，尝试上传到 MinIO
        if upload_to_minio and minio_storage_manager.is_configured():
            try:
                # 对于 SVG，需要先编码为 base64
                if output_type == "svg":
                    import base64
                    svg_base64 = base64.b64encode(chart_data.encode('utf-8')).decode('utf-8')
                    url = minio_storage_manager.upload_image_sync(svg_base64, f"{symbol}_chart_{output_type}", mime_type, timeout=30)
                else:
                    url = minio_storage_manager.upload_image_sync(base64_data, f"{symbol}_chart_{output_type}", mime_type, timeout=30)
                
                if url:
                    logger.info(f"图片已上传到 MinIO: {url}")
                    # 返回 JSON 格式
                    return json.dumps({"url": url}, ensure_ascii=False)
            except Exception as minio_error:
                logger.warning(f"MinIO 上传失败，返回 base64 内容: {minio_error}")
        
        # 尝试使用 MCP ImageContent 类型
        if MCP_IMAGE_AVAILABLE and ImageContent is not None:
            try:
                # 使用 MCP ImageContent 类型
                return ImageContent(type="image", data=base64_data, mimeType=mime_type)
            except Exception as e:
                logger.warning(f"Could not create MCP ImageContent object: {e}")
        
        # 回退到字典格式
        return [{
            "type": "image",
            "data": base64_data,
            "mimeType": mime_type
        }]
        
    except Exception as e:
        logger.error(f"Error generating chart image: {e}")
        # 返回错误信息
        return [{
            "type": "text",
            "text": f"生成图表图片失败: {str(e)}"
        }]

async def run_in_threadpool(func, *args, **kwargs):
    """Run a synchronous function in a threadpool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

def echarts_run(symbol: str, period: str = '1年', indicators: str = 'MA,MACD,KDJ,BOLL', frequency: str = 'daily', use_minio: bool = True) -> str:
    """生成ECharts HTML的核心函数，支持 MinIO 存储
    
    Args:
        symbol: 股票代码
        period: 分析周期
        indicators: 技术指标
        frequency: 数据频率
        use_minio: 是否尝试使用 MinIO 存储
    
    Returns:
        str: 如果 MinIO 可用返回 URL，否则返回 HTML 内容
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
        
        # 生成ECharts HTML
        visualizer = Visualizer()
        html_content = visualizer.create_echarts_html(
            stock_data, 
            indicators_data, 
            symbol, 
            requested_indicators,
            save_path,
            frequency
        )
        
        # 如果启用了 MinIO 且已配置，尝试上传到 MinIO
        if use_minio and minio_storage_manager.is_configured():
            try:
                # 使用工具类的同步方法上传
                url = minio_storage_manager.upload_html_sync(html_content, f"{symbol}_chart", timeout=30)
                
                if url:
                    logger.info(f"HTML 图表已上传到 MinIO: {url}")
                    # 返回 JSON 格式
                    return json.dumps({"url": url}, ensure_ascii=False)
                    
            except Exception as minio_error:
                logger.warning(f"MinIO 上传失败，返回 HTML 内容: {minio_error}")
        
        # 如果没有 MinIO 或上传失败，返回错误信息
        return f"请配置 MinIO 后重试"
        
    except Exception as e:
        logger.error(f"Error in echarts_run: {e}")
        return f"生成ECharts HTML失败: {str(e)}"

def chart_image_run(symbol: str, period: str = '1年', indicators: str = 'MA,MACD,KDJ,BOLL', frequency: str = 'daily', width: int = 800, height: int = 600, output_type: str = 'png') -> str:
    """生成图表图片的核心函数，返回：
    - PNG: base64编码的字符串
    - SVG: SVG字符串（未编码）
    """
    try:
        # 获取股票数据
        data_fetcher = StockDataFetcher()
        stock_data = data_fetcher.fetch_stock_data(symbol, period, frequency)
        
        if stock_data.empty:
            raise Exception("无法获取股票数据，请检查股票代码是否正确")
        
        # 计算技术指标
        technical_analyzer = TechnicalAnalyzer()
        indicators_data = technical_analyzer.calculate_indicators(stock_data)
        
        # 解析用户指定的指标
        requested_indicators = [ind.strip().upper() for ind in indicators.split(',')]
        
        # 生成图片
        image_generator = ImageGenerator()
        echarts_option = image_generator.convert_echarts_option_to_candlestick_format(
            stock_data, 
            indicators_data, 
            symbol, 
            requested_indicators,
            frequency
        )
        
        # 生成图片数据（返回base64字符串）
        base64_data = image_generator.generate_chart_image(
            echarts_option,
            width,
            height,
            "default",
            output_type,
            "generate_candlestick_image_chart",
            symbol,
            indicators
        )
        
        return base64_data
        
    except Exception as e:
        logger.error(f"Error in chart_image_run: {e}")
        raise

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

@mcp.tool()
async def chan_analysis(symbol: str, period: str = '1年', frequency: str = 'daily') -> str:
    """
    执行缠论技术分析，基于缠中说禅理论进行股票走势分析
    
    功能特性:
    - 基于缠论理论进行股票走势分析
    - 识别笔、线段、中枢等缠论核心概念
    - 分析买卖点和趋势转换
    - 提供缠论视角的技术分析报告
    - 支持多时间周期的缠论分析
    
    参数说明:
        symbol (str): A股股票代码，支持：
            - 主板股票：000001、600036等
            - 创业板股票：300001等
            - 科创板股票：688001等
        period (str): 分析周期，默认'1年'，可选：
            - '1年'、'6个月'、'3个月'、'1个月'、'1周'
        frequency (str): 数据频率，默认'daily'，可选：
            - 'daily'：日线（推荐用于缠论分析）
            - 'weekly'：周线
            - 'monthly'：月线
    
    返回值:
        str: 缠论分析报告，包含：
            - 笔的识别和分析
            - 线段的划分
            - 中枢的识别
            - 买卖点分析
            - 趋势判断和操作建议
    
    使用示例:
        # 对平安银行进行1年日线缠论分析
        result = await chan_analysis("000001", "1年", "daily")
        
        # 对招商银行进行6个月周线缠论分析
        result = await chan_analysis("600036", "6个月", "weekly")
        
        # 对创业板股票进行3个月日线缠论分析
        result = await chan_analysis("300001", "3个月", "daily")
    """
    try:
        analysis_result = await run_in_threadpool(chan_analysis_run, symbol=symbol, period=period, frequency=frequency)
        return analysis_result
    except Exception as e:
        logger.error(f"Error in chan analysis: {e}")
        return f"缠论分析失败: {str(e)}"

def chan_analysis_run(symbol: str, period: str = '1年', frequency: str = 'daily') -> str:
    """执行缠论分析的核心函数"""
    try:
        # 初始化缠论分析模块
        data_fetcher = StockDataFetcher()
        chan_analysis_engine = ChanAnalysisEngine()
        chan_visualizer = ChanVisualizer()
        
        # 获取股票数据
        stock_data = data_fetcher.fetch_stock_data(symbol, period, frequency)
        if stock_data.empty:
            return f"无法获取股票 {symbol} 的数据"
        
        # 执行缠论分析
        chan_analysis = chan_analysis_engine.advanced_chan_analysis(stock_data)
        
        # 生成分析报告
        chan_report = chan_visualizer.create_chan_analysis_report(chan_analysis, symbol)
        
        return chan_report
        
    except Exception as e:
        return f"缠论分析过程中出错: {str(e)}"


@mcp.tool()
async def chan_chart(symbol: str, period: str = '1年', frequency: str = 'daily') -> str:
    """
    生成缠论分析的可视化图表
    
    功能特性:
    - 生成包含缠论元素的K线图
    - 标注笔、线段、中枢等缠论结构
    - 显示买卖点和趋势线
    - 生成专业的缠论分析图表
    - 图表保存为PNG格式，便于查看和分享
    
    参数说明:
        symbol (str): A股股票代码，支持：
            - 主板股票：000001、600036等
            - 创业板股票：300001等
            - 科创板股票：688001等
        period (str): 分析周期，默认'1年'，可选：
            - '1年'、'6个月'、'3个月'、'1个月'、'1周'
        frequency (str): 数据频率，默认'daily'，可选：
            - 'daily'：日线（推荐用于缠论分析）
            - 'weekly'：周线
            - 'monthly'：月线
    
    返回值:
        str: 图表生成结果，包含：
            - 图表生成成功提示
            - 图表文件保存路径
            - 图表内容描述
    
    使用示例:
        # 生成平安银行1年日线缠论图表
        result = await chan_chart("000001", "1年", "daily")
        
        # 生成招商银行6个月周线缠论图表
        result = await chan_chart("600036", "6个月", "weekly")
        
        # 生成创业板股票3个月日线缠论图表
        result = await chan_chart("300001", "3个月", "daily")
    """
    try:
        chart_path = await run_in_threadpool(chan_chart_run, symbol=symbol, period=period, frequency=frequency)
        return f"缠论分析图表已生成: {chart_path}"
    except Exception as e:
        logger.error(f"Error generating chan chart: {e}")
        return f"生成缠论图表失败: {str(e)}"


def chan_chart_run(symbol: str, period: str = '1年', frequency: str = 'daily') -> str:
    """生成缠论分析图表的核心函数"""
    try:
        # 初始化模块
        data_fetcher = StockDataFetcher()
        chan_analysis_engine = ChanAnalysisEngine()
        chan_visualizer = ChanVisualizer()
        
        # 获取股票数据
        stock_data = data_fetcher.fetch_stock_data(symbol, period, frequency)
        if stock_data.empty:
            return f"无法获取股票 {symbol} 的数据"
        
        # 执行缠论分析
        chan_analysis = chan_analysis_engine.advanced_chan_analysis(stock_data)
        
        # 确保输出目录存在
        output_dir = f"./output/charts"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成缠论分析图表
        chart_path = chan_visualizer.create_comprehensive_chan_chart(
            stock_data, chan_analysis, 
            os.path.join(output_dir, f"{symbol}_chan_analysis.png")
        )
        
        return chart_path
        
    except Exception as e:
        return f"生成缠论图表过程中出错: {str(e)}"

if __name__ == "__main__":
    # mcp.run(transport='stdio')
    mcp.run(transport='streamable-http')
