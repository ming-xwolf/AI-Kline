"""
K线工具类，提供各种辅助函数和工具方法
"""
import logging
import asyncio
import json
from datetime import datetime, timedelta
import akshare as ak
import pandas as pd

from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.visualizer import Visualizer
from modules.ai_analyzer import AIAnalyzer
from modules.chan_analysis_engine import ChanAnalysisEngine
from modules.chan_visualizer import ChanVisualizer
from modules.image_generator import ImageGenerator
from modules.minio_storage import minio_storage_manager

logger = logging.getLogger(__name__)


class KlineUtils:
    """K线工具类，提供各种辅助函数"""
    
    @staticmethod
    def get_frequency_default_days():
        """获取各频率的默认周期（以天数表示）
        
        Returns:
            dict: 频率到默认天数的映射
        """
        return {
            'monthly': 3650,      # 月线默认10年
            'weekly': 730,        # 周线默认2年
            'daily': 730,         # 日线默认2年
            '60min': 90,          # 60分钟默认3个月
            '30min': 60,          # 30分钟默认2个月
            '15min': 30,          # 15分钟默认1个月
            '5min': 7,            # 5分钟默认1周
            '1min': 2             # 1分钟默认2天
        }
    
    @staticmethod
    def get_latest_trading_date(target_date: datetime = None) -> str:
        """获取最近的交易日
        
        Args:
            target_date: 目标日期，默认为今天
        
        Returns:
            str: 最近交易日的日期，格式为 'YYYYMMDD'
        """
        if target_date is None:
            target_date = datetime.now()
        
        try:
            # 尝试获取交易日历
            try:
                trade_cal = ak.tool_trade_date_hist_sina()
                if not trade_cal.empty:
                    # akshare 返回的列名可能是 'trade_date' 或 '日期' 等，尝试多种可能
                    date_col = None
                    for col in ['trade_date', '日期', 'date', 'Date']:
                        if col in trade_cal.columns:
                            date_col = col
                            break
                    
                    if date_col:
                        # 转换为日期格式
                        trade_dates = pd.to_datetime(trade_cal[date_col].astype(str), format='%Y%m%d', errors='coerce')
                        # 过滤掉无效日期
                        trade_dates = trade_dates.dropna()
                        # 找到小于等于目标日期的最近交易日
                        valid_dates = trade_dates[trade_dates <= target_date]
                        if not valid_dates.empty:
                            latest_date = valid_dates.max()
                            return latest_date.strftime('%Y%m%d')
            except Exception as e:
                logger.warning(f"无法获取交易日历，使用简单判断: {e}")
            
            # 回退方案：简单判断（跳过周末）
            current = target_date
            max_days_back = 7  # 最多往前找7天
            for _ in range(max_days_back):
                # 周一=0, 周日=6，周一到周五是交易日
                if current.weekday() < 5:  # 0-4 是周一到周五
                    return current.strftime('%Y%m%d')
                current = current - timedelta(days=1)
            
            # 如果都没找到，返回7天前（应该能找到）
            return (target_date - timedelta(days=7)).strftime('%Y%m%d')
            
        except Exception as e:
            logger.error(f"获取最近交易日失败: {e}")
            # 最后的回退：返回昨天
            yesterday = target_date - timedelta(days=1)
            return yesterday.strftime('%Y%m%d')
    
    @staticmethod
    def calculate_start_date_by_frequency(frequency: str) -> tuple[str, str]:
        """根据频率的默认周期计算开始日期和结束日期
        
        Args:
            frequency: 数据频率，如 'daily', 'weekly', 'monthly', '1min', '5min', '15min', '30min', '60min'
        
        Returns:
            tuple[str, str]: (开始日期, 结束日期)，格式为 'YYYYMMDD'
        """
        # 获取最近的交易日作为结束日期
        end_date_str = KlineUtils.get_latest_trading_date()
        end_date = datetime.strptime(end_date_str, '%Y%m%d')
        
        # 获取频率的默认周期
        frequency_default_period = KlineUtils.get_frequency_default_days()
        
        if frequency not in frequency_default_period:
            # 默认返回1年的数据
            default_days = 365
        else:
            default_days = frequency_default_period[frequency]
        
        # 计算开始日期
        start_date = end_date - timedelta(days=default_days)
        start_date_str = start_date.strftime('%Y%m%d')
        
        return start_date_str, end_date_str
    
    @staticmethod
    async def run_in_threadpool(func, *args, **kwargs):
        """Run a synchronous function in a threadpool."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    @staticmethod
    def echarts_run(symbol: str, period: str = '1年', indicators: str = 'MA,MACD,KDJ,BOLL', frequency: str = 'daily', use_minio: bool = True) -> str:
        """生成ECharts HTML的核心函数，支持 MinIO 存储
        
        Args:
            symbol: 股票代码
            period: 分析周期
            indicators: 技术指标
            frequency: 数据频率
            use_minio: 是否尝试使用 MinIO 存储
        
        Returns:
            str: 如果 MinIO 可用返回 URL 字符串，否则返回错误信息字符串
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
                        # 只返回 URL 字符串
                        return url
                        
                except Exception as minio_error:
                    logger.warning(f"MinIO 上传失败，返回 HTML 内容: {minio_error}")
            
            # 如果没有 MinIO 或上传失败，返回错误信息
            return f"请配置 MinIO 后重试"
            
        except Exception as e:
            logger.error(f"Error in echarts_run: {e}")
            return f"生成ECharts HTML失败: {str(e)}"
    
    @staticmethod
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
    
    @staticmethod
    def pattern_run(symbol: str, period: str = '1年', save_path: str = './output', frequency: str = 'daily') -> str:
        """执行全面技术分析的核心函数"""
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
    
    @staticmethod
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
    
    @staticmethod
    def chan_chart_run(symbol: str, period: str = '1年', frequency: str = 'daily') -> str:
        """生成缠论分析图表的核心函数"""
        try:
            # 初始化模块
            import os
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
    
    @staticmethod
    def get_quote_run(symbol: str, frequency: str = 'daily') -> str:
        """
        获取股票行情数据的核心函数
        
        Args:
            symbol: 股票代码
            frequency: 数据频率
            
        Returns:
            str: JSON格式的股票数据
        """
        # 根据频率的默认周期计算开始日期和结束日期
        start_date, end_date = KlineUtils.calculate_start_date_by_frequency(frequency)
        
        data_fetcher = StockDataFetcher()
        # 使用 date_as_string=True 让数据获取时就返回字符串格式的日期
        stock_data = data_fetcher.fetch_stock_data_by_date_range(symbol, start_date, end_date, frequency, date_as_string=True)
        
        if stock_data.empty:
            return json.dumps({
                "error": "数据获取失败",
                "message": "无法获取股票数据，请检查股票代码是否正确"
            }, ensure_ascii=False)
        
        # 将 DataFrame 转换为字典，然后转换为 JSON 字符串
        # 日期已经是字符串格式，无需额外处理
        analysis_result = stock_data.to_dict()
        
        return json.dumps(analysis_result, ensure_ascii=False, default=str)
    
    @staticmethod
    def get_news_run(symbol: str) -> str:
        """
        获取股票新闻数据的核心函数
        
        Args:
            symbol: 股票代码
            
        Returns:
            str: JSON格式的新闻数据
        """
        financial_data = {}
        data_fetcher = StockDataFetcher()
        news_data = data_fetcher.fetch_news_data(symbol)
        financial_data['news'] = news_data
        return json.dumps(financial_data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_financial_run(symbol: str) -> str:
        """
        获取股票财务数据的核心函数
        
        Args:
            symbol: 股票代码
            
        Returns:
            str: JSON格式的财务数据
        """
        data_fetcher = StockDataFetcher()
        financial_data = data_fetcher.fetch_financial_data(symbol)
        return json.dumps(financial_data, ensure_ascii=False, indent=2, default=str)
    
    @staticmethod
    def get_sector_info_run(symbol: str) -> str:
        """
        获取股票板块信息的核心函数
        
        Args:
            symbol: 股票代码
            
        Returns:
            str: JSON格式的板块信息
        """
        data_fetcher = StockDataFetcher()
        sector_info = data_fetcher.fetch_sector_info(symbol)
        return json.dumps(sector_info, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_basic_info_run(symbol: str) -> str:
        """
        获取股票基本信息的核心函数
        
        Args:
            symbol: 股票代码
            
        Returns:
            str: JSON格式的基本信息
        """
        data_fetcher = StockDataFetcher()
        basic_info = data_fetcher.fetch_stock_basic_info(symbol)
        return json.dumps(basic_info, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_shareholder_info_run(symbol: str) -> str:
        """
        获取股东信息的核心函数
        
        Args:
            symbol: 股票代码
            
        Returns:
            str: JSON格式的股东信息
        """
        data_fetcher = StockDataFetcher()
        shareholder_info = data_fetcher.fetch_shareholder_info(symbol)
        return json.dumps(shareholder_info, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_all_stocks_run() -> str:
        """
        获取所有股票列表的核心函数
        
        Returns:
            str: JSON格式的股票列表
        """
        data_fetcher = StockDataFetcher()
        stock_list_info = data_fetcher.fetch_all_stock_list()
        return json.dumps(stock_list_info, ensure_ascii=False, indent=2)

