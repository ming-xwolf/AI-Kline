import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
from tqdm import tqdm

class StockDataFetcher:
    """
    股票数据获取类，负责从AKShare获取股票的历史K线数据、财务数据和新闻信息
    """
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y%m%d')
    
    def _normalize_stock_code(self, stock_code: str) -> str:
        """格式化股票代码，移除前缀和后缀
        
        Args:
            stock_code: 股票代码，如 '000001', 'sz000001', '000001.sz' 等
            
        Returns:
            str: 格式化后的股票代码
        """
        if not stock_code.isdigit():
            # 取消前缀sz或者sh
            stock_code = stock_code.lstrip('sz').lstrip('sh').rstrip('SZ').rstrip('SH')
            # 取消后缀.sz或者.sh
            stock_code = stock_code.rstrip('.sz').rstrip('.sh').rstrip('.SZ').rstrip('.SH')
        return stock_code
    
    def _rename_columns(self, stock_data: pd.DataFrame, frequency: str, date_as_string: bool = False) -> pd.DataFrame:
        """重命名列以便后续处理
        
        Args:
            stock_data: 股票数据DataFrame
            frequency: 数据频率
            date_as_string: 是否将日期列转换为字符串格式（默认False，保持datetime格式以便后续处理）
            
        Returns:
            pd.DataFrame: 重命名后的DataFrame
        """
        if frequency in ['1min', '5min', '15min', '30min', '60min']:
            # 分钟级数据的列名映射
            stock_data.rename(columns={
                '时间': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '均价': 'avg_price'
            }, inplace=True)
        else:
            # 日线、周线、月线数据的列名映射
            stock_data.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover'
            }, inplace=True)
        
        # 处理日期列
        if 'date' in stock_data.columns:
            is_minute_frequency = frequency in ['1min', '5min', '15min', '30min', '60min']
            
            if date_as_string:
                # 转换为字符串格式（用于JSON序列化）
                if is_minute_frequency:
                    # 分钟级数据保留完整时间信息（YYYY-MM-DD HH:MM:SS）
                    stock_data['date'] = pd.to_datetime(stock_data['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # 日线、周线、月线数据只保留日期（YYYY-MM-DD）
                    stock_data['date'] = pd.to_datetime(stock_data['date']).dt.strftime('%Y-%m-%d')
            else:
                # 转换为日期时间格式（用于技术分析、图表生成等）
                stock_data['date'] = pd.to_datetime(stock_data['date'])
        
        return stock_data
    
    def fetch_stock_data_by_date_range(self, stock_code: str, start_date: str, end_date: str, frequency: str = 'daily', date_as_string: bool = False):
        """
        通过指定的日期范围获取股票的历史K线数据
        
        参数:
            stock_code (str): 股票代码，如 '000001'
            start_date (str): 开始日期，格式为 'YYYYMMDD'
            end_date (str): 结束日期，格式为 'YYYYMMDD'
            frequency (str): 数据频率，支持 'daily', 'weekly', 'monthly', '1min', '5min', '15min', '30min', '60min'
            date_as_string (bool): 是否将日期列转换为字符串格式（默认False，保持datetime格式）
            
        返回:
            pandas.DataFrame: 包含股票历史数据的DataFrame
        """
        # 格式化股票代码
        stock_code = self._normalize_stock_code(stock_code)
        
        try:
            # 根据频率选择不同的akshare函数
            if frequency in ['1min', '5min', '15min', '30min', '60min']:
                # 分钟级数据使用不同的函数
                period_map = {
                    '1min': '1',
                    '5min': '5', 
                    '15min': '15',
                    '30min': '30',
                    '60min': '60'
                }
                # 分钟级数据需要调整开始日期格式
                start_datetime = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d 09:30:00')
                end_datetime = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d %H:%M:%S')
                
                stock_data = ak.stock_zh_a_hist_min_em(
                    symbol=stock_code, 
                    period=period_map[frequency],
                    start_date=start_datetime, 
                    end_date=end_datetime, 
                    adjust="qfq"
                )
            else:
                # 日线、周线、月线数据
                period_map = {
                    'daily': 'daily',
                    'weekly': 'weekly', 
                    'monthly': 'monthly'
                }
                stock_data = ak.stock_zh_a_hist(
                    symbol=stock_code, 
                    period=period_map.get(frequency, 'daily'), 
                    start_date=start_date, 
                    end_date=end_date, 
                    adjust="qfq"
                )
            
            # 重命名列
            stock_data = self._rename_columns(stock_data, frequency, date_as_string=date_as_string)
            
            return stock_data
            
        except Exception as e:
            print(f"获取股票数据时出错: {e}")
            return pd.DataFrame()
    
    def fetch_stock_data(self, stock_code, period='1年', frequency='daily'):
        """
        获取股票的历史K线数据（使用period参数，兼容旧接口）
        
        参数:
            stock_code (str): 股票代码，如 '000001'
            period (str): 获取数据的时间周期，默认为'1年'
            frequency (str): 数据频率，支持 'daily', 'weekly', 'monthly', '1min', '5min', '15min', '30min', '60min'
            
        返回:
            pandas.DataFrame: 包含股票历史数据的DataFrame
            
        注意:
            此方法内部调用 fetch_stock_data_by_date_range 方法
        """
        
        # 计算开始日期
        if period == '1年':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        elif period == '6个月':
            start_date = (datetime.now() - timedelta(days=183)).strftime('%Y%m%d')
        elif period == '3个月':
            start_date = (datetime.now() - timedelta(days=91)).strftime('%Y%m%d')
        elif period == '1个月':
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        elif period == '1周':
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        else:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        # 使用新的方法获取数据
        return self.fetch_stock_data_by_date_range(stock_code, start_date, self.today, frequency)
    
    def fetch_financial_data(self, stock_code):
        """
        获取股票的财务数据（包括详细财务报表）
        
        参数:
            stock_code (str): 股票代码，如 '000001'
            
        返回:
            dict: 包含财务数据的字典，包括：
                - 基本信息：股票基本信息
                - 关键指标：最新财务指标摘要
                - 资产负债表：最近几个报告期的资产负债表数据
                - 利润表：最近几个报告期的利润表数据
                - 现金流量表：最近几个报告期的现金流量表数据
                - 财务指标：详细的财务分析指标
        """
        financial_data = {
            '股票代码': stock_code,
            '基本信息': {},
            '关键指标': {},
            '资产负债表': [],
            '利润表': [],
            '现金流量表': [],
            '财务指标': []
        }
        
        try:
            # 确保股票代码格式正确
            if not stock_code.isdigit():
                stock_code = stock_code.lstrip('sz').lstrip('sh').rstrip('SZ').rstrip('SH')
                stock_code = stock_code.rstrip('.sz').rstrip('.sh').rstrip('.SZ').rstrip('.SH')
            
            financial_data['股票代码'] = stock_code
            
            # 为资产负债表、利润表、现金流量表API准备带前缀的股票代码
            # 这些API需要 'SZ' 或 'SH' 前缀
            if stock_code.startswith(('0', '3')):
                # 深市股票（000、001、002、300等）
                prefixed_code = f'SZ{stock_code}'
            elif stock_code.startswith(('6', '9')):
                # 沪市股票（600、601、603、688、900等）
                prefixed_code = f'SH{stock_code}'
            else:
                prefixed_code = stock_code
            
            # 1. 获取股票基本信息
            try:
                stock_info = ak.stock_individual_info_em(symbol=stock_code)
                if not stock_info.empty:
                    financial_data['基本信息'] = stock_info.set_index('item').to_dict()['value']
            except Exception as e:
                print(f"获取基本信息时出错: {e}")
            
            # 2. 获取关键指标摘要
            try:
                financial_abstract = ak.stock_financial_abstract(symbol=stock_code)
                if not financial_abstract.empty:
                    # 转换为字典格式，保留所有列
                    indicators_dict = {}
                    for _, row in financial_abstract.iterrows():
                        indicator_name = row.iloc[0] if len(row) > 0 else ''
                        if indicator_name:
                            # 获取所有报告期的数据
                            values = {}
                            for i in range(1, len(row)):
                                col_name = financial_abstract.columns[i] if i < len(financial_abstract.columns) else f'报告期{i}'
                                values[col_name] = row.iloc[i] if i < len(row) else None
                            indicators_dict[indicator_name] = values
                    financial_data['关键指标'] = indicators_dict
            except Exception as e:
                print(f"获取关键指标时出错: {e}")
            
            # 3. 获取资产负债表（最近3个报告期）
            try:
                balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=prefixed_code)
                if balance_sheet is not None and not balance_sheet.empty:
                    # 数据格式：每行是一个报告期，每列是一个财务项目
                    # 我们只需要最近3个报告期的数据
                    recent_rows = balance_sheet.head(3) if len(balance_sheet) > 3 else balance_sheet
                    
                    # 获取报告日期列
                    report_date_col = 'REPORT_DATE' if 'REPORT_DATE' in balance_sheet.columns else None
                    report_type_col = 'REPORT_TYPE' if 'REPORT_TYPE' in balance_sheet.columns else None
                    
                    balance_data = []
                    # 遍历每个报告期
                    for idx, row in recent_rows.iterrows():
                        period_data = {
                            '报告日期': str(row[report_date_col]) if report_date_col else f'报告期{idx+1}',
                            '报告类型': str(row[report_type_col]) if report_type_col else '',
                            '数据': {}
                        }
                        # 遍历所有财务项目列（跳过元数据列）
                        skip_cols = ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE', 
                                    'ORG_TYPE', 'REPORT_DATE', 'REPORT_TYPE', 'REPORT_DATE_NAME', 
                                    'SECURITY_TYPE_CODE', 'NOTICE_DATE', 'LISTING_STATE']
                        
                        for col in balance_sheet.columns:
                            if col not in skip_cols:
                                value = row[col]
                                if pd.notna(value):
                                    period_data['数据'][col] = value
                        
                        balance_data.append(period_data)
                    financial_data['资产负债表'] = balance_data
            except Exception as e:
                print(f"获取资产负债表时出错: {e}")
            
            # 4. 获取利润表（最近3个报告期）
            try:
                profit_sheet = ak.stock_profit_sheet_by_report_em(symbol=prefixed_code)
                if profit_sheet is not None and not profit_sheet.empty:
                    # 数据格式：每行是一个报告期，每列是一个财务项目
                    recent_rows = profit_sheet.head(3) if len(profit_sheet) > 3 else profit_sheet
                    
                    report_date_col = 'REPORT_DATE' if 'REPORT_DATE' in profit_sheet.columns else None
                    report_type_col = 'REPORT_TYPE' if 'REPORT_TYPE' in profit_sheet.columns else None
                    
                    profit_data = []
                    for idx, row in recent_rows.iterrows():
                        period_data = {
                            '报告日期': str(row[report_date_col]) if report_date_col else f'报告期{idx+1}',
                            '报告类型': str(row[report_type_col]) if report_type_col else '',
                            '数据': {}
                        }
                        skip_cols = ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE', 
                                    'ORG_TYPE', 'REPORT_DATE', 'REPORT_TYPE', 'REPORT_DATE_NAME', 
                                    'SECURITY_TYPE_CODE', 'NOTICE_DATE', 'LISTING_STATE']
                        
                        for col in profit_sheet.columns:
                            if col not in skip_cols:
                                value = row[col]
                                if pd.notna(value):
                                    period_data['数据'][col] = value
                        
                        profit_data.append(period_data)
                    financial_data['利润表'] = profit_data
            except Exception as e:
                print(f"获取利润表时出错: {e}")
            
            # 5. 获取现金流量表（最近3个报告期）
            try:
                cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=prefixed_code)
                if cash_flow is not None and not cash_flow.empty:
                    # 数据格式：每行是一个报告期，每列是一个财务项目
                    recent_rows = cash_flow.head(3) if len(cash_flow) > 3 else cash_flow
                    
                    report_date_col = 'REPORT_DATE' if 'REPORT_DATE' in cash_flow.columns else None
                    report_type_col = 'REPORT_TYPE' if 'REPORT_TYPE' in cash_flow.columns else None
                    
                    cash_flow_data = []
                    for idx, row in recent_rows.iterrows():
                        period_data = {
                            '报告日期': str(row[report_date_col]) if report_date_col else f'报告期{idx+1}',
                            '报告类型': str(row[report_type_col]) if report_type_col else '',
                            '数据': {}
                        }
                        skip_cols = ['SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE', 
                                    'ORG_TYPE', 'REPORT_DATE', 'REPORT_TYPE', 'REPORT_DATE_NAME', 
                                    'SECURITY_TYPE_CODE', 'NOTICE_DATE', 'LISTING_STATE']
                        
                        for col in cash_flow.columns:
                            if col not in skip_cols:
                                value = row[col]
                                if pd.notna(value):
                                    period_data['数据'][col] = value
                        
                        cash_flow_data.append(period_data)
                    financial_data['现金流量表'] = cash_flow_data
            except Exception as e:
                print(f"获取现金流量表时出错: {e}")
            
            # 6. 获取财务分析指标（最近几个报告期）
            try:
                # 使用正确的参数：symbol
                financial_indicators = ak.stock_financial_analysis_indicator(symbol=stock_code, start_year='2020')
                if financial_indicators is not None and not financial_indicators.empty:
                    # 转换为字典列表格式
                    indicators_list = []
                    for _, row in financial_indicators.iterrows():
                        indicator_dict = {}
                        for col in financial_indicators.columns:
                            value = row[col]
                            # 处理 NaN 值
                            if pd.notna(value):
                                indicator_dict[str(col)] = value
                            else:
                                indicator_dict[str(col)] = None
                        indicators_list.append(indicator_dict)
                    # 只保留最近5个报告期的数据
                    financial_data['财务指标'] = indicators_list[-5:] if len(indicators_list) > 5 else indicators_list
            except Exception as e:
                print(f"获取财务分析指标时出错: {e}")
            
            return financial_data
            
        except Exception as e:
            print(f"获取财务数据时出错: {e}")
            financial_data['错误信息'] = str(e)
            return financial_data
    
    def fetch_news_data(self, stock_code, max_items=10):
        """
        获取与股票相关的新闻信息
        
        参数:
            stock_code (str): 股票代码，如 '000001'
            max_items (int): 最大获取新闻条数
            
        返回:
            list: 包含新闻数据的列表
        """
        news_list = []
        
        try:
            # 获取股票名称
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                stock_name = stock_info.loc[stock_info['item'] == '股票简称', 'value'].values[0]
                
                # 获取股票相关新闻
                news_data = ak.stock_news_em(symbol=stock_code)
                
                if not news_data.empty:
                    # 限制新闻条数
                    news_data = news_data.head(max_items)
                    
                    for _, row in news_data.iterrows():
                        news_item = {
                            'title': row['新闻标题'],
                            'date': row['发布时间'],
                            'content': row['新闻内容'] if '新闻内容' in row else '',
                        }
                        news_list.append(news_item)
                
            return news_list
            
        except Exception as e:
            print(f"获取新闻数据时出错: {e}")
            return news_list
    
    def fetch_sector_info(self, stock_code):
        """
        获取个股所属板块信息（行业板块和概念板块）
        
        参数:
            stock_code (str): 股票代码，如 '000001'
            
        返回:
            dict: 包含板块信息的字典，包括：
                - 基本信息（股票代码、股票名称、所属行业等）
                - 行业板块列表
                - 概念板块列表
        """
        sector_info = {
            '股票代码': stock_code,
            '股票名称': '',
            '所属行业': '',
            '行业板块': [],
            '概念板块': [],
            '备注': ''
        }
        
        try:
            # 确保股票代码格式正确
            if not stock_code.isdigit():
                stock_code = stock_code.lstrip('sz').lstrip('sh').rstrip('SZ').rstrip('SH')
                stock_code = stock_code.rstrip('.sz').rstrip('.sh').rstrip('.SZ').rstrip('.SH')
            
            sector_info['股票代码'] = stock_code
            
            # 获取股票基本信息（包含所属行业）
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                info_dict = stock_info.set_index('item').to_dict()['value']
                sector_info['股票名称'] = info_dict.get('股票简称', '')
                sector_info['所属行业'] = info_dict.get('所属行业', '')
            
            # 获取股票所属的概念板块
            # 注意：遍历所有板块可能较慢，建议后续优化为缓存机制
            try:
                concept_board_list = ak.stock_board_concept_name_em()
                if not concept_board_list.empty and '板块名称' in concept_board_list.columns:
                    # 限制遍历数量以提高性能，或者可以根据需要调整
                    max_check = min(100, len(concept_board_list))  # 最多检查前100个概念板块
                    for _, board_row in concept_board_list.head(max_check).iterrows():
                        board_name = board_row['板块名称']
                        try:
                            # 获取该概念板块的成分股列表
                            cons_stocks = ak.stock_board_concept_cons_em(symbol=board_name)
                            if not cons_stocks.empty and '代码' in cons_stocks.columns:
                                # 检查该股票是否在成分股列表中
                                if stock_code in cons_stocks['代码'].values:
                                    sector_info['概念板块'].append(board_name)
                            # 添加小延迟避免请求过快
                            time.sleep(0.1)
                        except Exception as e:
                            # 某些板块可能无法获取成分股，跳过
                            continue
                    if len(concept_board_list) > max_check:
                        sector_info['备注'] = f'概念板块仅检查了前{max_check}个，共{len(concept_board_list)}个'
            except Exception as e:
                print(f"获取概念板块信息时出错: {e}")
                sector_info['备注'] = f"获取概念板块信息时出错: {str(e)}"
            
            # 获取股票所属的行业板块
            try:
                industry_board_list = ak.stock_board_industry_name_em()
                if not industry_board_list.empty and '板块名称' in industry_board_list.columns:
                    # 限制遍历数量以提高性能
                    max_check = min(50, len(industry_board_list))  # 最多检查前50个行业板块
                    for _, board_row in industry_board_list.head(max_check).iterrows():
                        board_name = board_row['板块名称']
                        try:
                            # 获取该行业板块的成分股列表
                            cons_stocks = ak.stock_board_industry_cons_em(symbol=board_name)
                            if not cons_stocks.empty and '代码' in cons_stocks.columns:
                                # 检查该股票是否在成分股列表中
                                if stock_code in cons_stocks['代码'].values:
                                    sector_info['行业板块'].append(board_name)
                            # 添加小延迟避免请求过快
                            time.sleep(0.1)
                        except Exception as e:
                            # 某些板块可能无法获取成分股，跳过
                            continue
            except Exception as e:
                print(f"获取行业板块信息时出错: {e}")
                if sector_info['备注']:
                    sector_info['备注'] += f"; 获取行业板块信息时出错: {str(e)}"
                else:
                    sector_info['备注'] = f"获取行业板块信息时出错: {str(e)}"
            
            return sector_info
            
        except Exception as e:
            error_msg = f"获取板块信息时出错: {str(e)}"
            print(error_msg)
            sector_info['备注'] = error_msg
            return sector_info
    
    def fetch_stock_basic_info(self, stock_code):
        """
        获取个股基本信息
        
        参数:
            stock_code (str): 股票代码，如 '000001'
            
        返回:
            dict: 包含股票基本信息的字典，包括：
                - 股票代码、股票简称
                - 所属行业
                - 最新价
                - 总市值、流通市值
                - 上市日期、注册资本等基本信息
        """
        basic_info = {
            '股票代码': stock_code,
            '股票简称': '',
            '所属行业': '',
            '最新价': '',
            '总市值': '',
            '流通市值': '',
            '上市日期': '',
            '注册资本': '',
            '详细信息': {}
        }
        
        try:
            # 确保股票代码格式正确
            if not stock_code.isdigit():
                stock_code = stock_code.lstrip('sz').lstrip('sh').rstrip('SZ').rstrip('SH')
                stock_code = stock_code.rstrip('.sz').rstrip('.sh').rstrip('.SZ').rstrip('.SH')
            
            basic_info['股票代码'] = stock_code
            
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                info_dict = stock_info.set_index('item').to_dict()['value']
                
                # 保存所有详细信息
                basic_info['详细信息'] = info_dict
                
                # 提取常用字段（支持多种字段名变体）
                basic_info['股票简称'] = info_dict.get('股票简称', '')
                basic_info['所属行业'] = (
                    info_dict.get('所属行业', '') or 
                    info_dict.get('所处行业', '') or 
                    info_dict.get('行业', '')
                )
                # 辅助函数：安全获取字段值（支持多种字段名）
                def safe_get(*keys, default=''):
                    for key in keys:
                        value = info_dict.get(key, default)
                        if value and str(value).strip():
                            return str(value)
                    return default
                
                basic_info['最新价'] = safe_get('最新价', '最新')
                basic_info['总市值'] = safe_get('总市值')
                basic_info['流通市值'] = safe_get('流通市值')
                basic_info['上市日期'] = safe_get('上市日期', '上市时间')
                basic_info['注册资本'] = safe_get('注册资本', '总股本')
            
            return basic_info
            
        except Exception as e:
            error_msg = f"获取股票基本信息时出错: {str(e)}"
            print(error_msg)
            basic_info['错误信息'] = error_msg
            return basic_info