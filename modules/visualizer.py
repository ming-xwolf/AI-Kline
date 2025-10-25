import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid
from pyecharts.commons.utils import JsCode

class Visualizer:
    """
    可视化类，负责生成K线图和各种技术指标图表
    """
    
    def __init__(self):
        # 设置matplotlib中文显示
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    def create_charts(self, stock_data, indicators, stock_code, save_path, frequency="daily"):
        """
        创建K线图和技术指标图表
        
        参数:
            stock_data (pandas.DataFrame): 股票历史数据
            indicators (dict): 技术指标数据
            stock_code (str): 股票代码
            save_path (str): 保存路径
            frequency (str): 数据频率，用于显示在标题中
            
        返回:
            str: 图表保存路径
        """
        if stock_data.empty:
            return ""
        
        # 获取股票名称
        try:
            import akshare as ak
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                stock_name = stock_info.loc[stock_info['item'] == '股票简称', 'value'].values[0]
            else:
                stock_name = stock_code
        except:
            stock_name = stock_code
        
        # 获取频率的中文显示
        frequency_display = self._get_frequency_display(frequency)
        
        # 创建保存目录
        chart_dir = os.path.join(save_path, 'charts')
        os.makedirs(chart_dir, exist_ok=True)
        
        # 使用matplotlib创建图表
        self._create_matplotlib_charts(stock_data, indicators, stock_code, stock_name, chart_dir, frequency)
        
        # 使用pyecharts创建交互式图表
        self._create_pyecharts_charts(stock_data, indicators, stock_code, stock_name, chart_dir, frequency_display)
        
        return chart_dir
    
    def _create_matplotlib_charts(self, stock_data, indicators, stock_code, stock_name, save_path, frequency="daily"):
        """
        使用matplotlib创建图表
        """
        # 获取英文频率显示
        frequency_display_en = self._get_frequency_display_en(frequency)
        
        # 创建一个大图，包含多个子图
        fig = plt.figure(figsize=(16, 12))
        
        # 设置网格
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1])
        
        # 添加K线图和移动平均线
        ax1 = fig.add_subplot(gs[0])
        ax1.set_title(f"{stock_code} {frequency_display_en}K-Line Chart & Technical Indicators")
        
        # 绘制K线图
        for i in range(len(stock_data)):
            # 绘制蜡烛图
            if stock_data['close'].iloc[i] >= stock_data['open'].iloc[i]:
                # 收盘价大于等于开盘价，为阳线
                color = 'red'
            else:
                # 收盘价小于开盘价，为阴线
                color = 'green'
            
            # 绘制实体部分
            ax1.plot([i, i], [stock_data['open'].iloc[i], stock_data['close'].iloc[i]], 
                     color=color, linewidth=8, solid_capstyle='butt')
            # 绘制上下影线
            ax1.plot([i, i], [stock_data['low'].iloc[i], stock_data['high'].iloc[i]], 
                     color=color, linewidth=1)
        
        # 绘制移动平均线
        ax1.plot(indicators['MA5'], label='MA5', linewidth=1)
        ax1.plot(indicators['MA10'], label='MA10', linewidth=1)
        ax1.plot(indicators['MA20'], label='MA20', linewidth=1)
        ax1.plot(indicators['MA30'], label='MA30', linewidth=1)
        
        # 绘制布林带
        ax1.plot(indicators['BOLL_upper'], label='BOLL Upper', linestyle='--', linewidth=1)
        ax1.plot(indicators['BOLL_middle'], label='BOLL Middle', linestyle='-', linewidth=1)
        ax1.plot(indicators['BOLL_lower'], label='BOLL Lower', linestyle='--', linewidth=1)
        
        # 设置x轴刻度
        ax1.set_xticks(range(0, len(stock_data), len(stock_data) // 10))
        ax1.set_xticklabels([d.strftime('%Y-%m-%d') for d in stock_data['date'].iloc[::len(stock_data) // 10]])
        ax1.legend(loc='best')
        ax1.grid(True)
        
        # 添加成交量图
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax2.set_title("Volume")
        for i in range(len(stock_data)):
            if stock_data['close'].iloc[i] >= stock_data['open'].iloc[i]:
                color = 'red'
            else:
                color = 'green'
            ax2.bar(i, stock_data['volume'].iloc[i], color=color, width=0.8)
        
        # 绘制成交量移动平均线
        ax2.plot(indicators['volume_ma5'], label='Volume MA5', color='blue', linewidth=1)
        ax2.plot(indicators['volume_ma10'], label='Volume MA10', color='orange', linewidth=1)
        ax2.legend(loc='best')
        ax2.grid(True)
        
        # 添加MACD图
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        ax3.set_title("MACD")
        ax3.plot(indicators['MACD'], label='MACD', color='blue', linewidth=1)
        ax3.plot(indicators['MACD_signal'], label='Signal', color='orange', linewidth=1)
        
        # 绘制MACD柱状图
        for i in range(len(indicators['MACD_hist'])):
            if indicators['MACD_hist'].iloc[i] >= 0:
                color = 'red'
            else:
                color = 'green'
            ax3.bar(i, indicators['MACD_hist'].iloc[i], color=color, width=0.8)
        
        ax3.legend(loc='best')
        ax3.grid(True)
        
        # 添加KDJ图
        ax4 = fig.add_subplot(gs[3], sharex=ax1)
        ax4.set_title("KDJ")
        ax4.plot(indicators['K'], label='K', color='blue', linewidth=1)
        ax4.plot(indicators['D'], label='D', color='orange', linewidth=1)
        ax4.plot(indicators['J'], label='J', color='green', linewidth=1)
        ax4.axhline(y=80, color='r', linestyle='--', alpha=0.3)
        ax4.axhline(y=20, color='g', linestyle='--', alpha=0.3)
        ax4.legend(loc='best')
        ax4.grid(True)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(os.path.join(save_path, f"{stock_code}_technical_analysis.png"), dpi=300)
        plt.close()
    
    def _create_pyecharts_charts(self, stock_data, indicators, stock_code, stock_name, save_path, frequency_display=""):
        """
        使用pyecharts创建交互式图表
        """
        # 准备基础数据
        dates, k_data = self._prepare_chart_data(stock_data)
        
        # 创建K线图和MA线
        overlap_kline = self._create_kline_with_ma(dates, k_data, indicators, stock_name, stock_code, frequency_display)
        
        # 创建成交量图
        volume_bar = self._create_volume_chart(dates, stock_data)
        
        # 创建网格布局并保存
        grid = Grid(init_opts=opts.InitOpts(
            width="100%",
            height="700px",
            page_title=f"AI看线 - {stock_name}({stock_code}) {frequency_display}技术分析"
        ))
        
        # 添加图表到网格
        grid.add(overlap_kline, grid_opts=opts.GridOpts(
            pos_left="10%", 
            pos_right="8%", 
            pos_top="10%",
            height="60%"
        ))
        
        grid.add(volume_bar, grid_opts=opts.GridOpts(
            pos_left="10%", 
            pos_right="8%", 
            pos_top="75%",
            height="20%"
        ))
        
        # 保存图表
        html_path = os.path.join(save_path, f"{stock_code}_interactive_chart.html")
        grid.render(html_path)
        
        # 优化HTML文件
        self._optimize_html_file(html_path)
    
    def create_echarts_html(self, stock_data, indicators, stock_code, requested_indicators, save_path="./output", frequency="daily"):
        """
        创建包含指定技术指标的ECharts HTML
        
        参数:
            stock_data (pandas.DataFrame): 股票历史数据
            indicators (dict): 技术指标数据
            stock_code (str): 股票代码
            requested_indicators (list): 用户请求的技术指标列表
            save_path (str): 保存路径，默认为"./output"
            frequency (str): 数据频率，用于显示在标题中
            
        返回:
            str: HTML内容
        """
        if stock_data.empty:
            return "<html><body><h1>无法获取股票数据</h1></body></html>"
        
        # 获取股票名称
        stock_name = self._get_stock_name(stock_code)
        
        # 获取频率的中文显示
        frequency_display = self._get_frequency_display(frequency)
        
        # 准备基础数据
        dates, k_data = self._prepare_chart_data(stock_data)
        
        # 计算动态高度和xaxis_index范围
        base_height = 500  # 增加基础高度，确保X轴完全显示
        chart_height = 350  # 增加每个图表的高度
        subplot_count = self._calculate_subplot_count(requested_indicators)
        dynamic_height = base_height + (subplot_count * chart_height)
        xaxis_range = list(range(subplot_count))
        
        # 创建K线图并添加技术指标
        overlap_kline = self._create_kline_with_indicators(dates, k_data, indicators, stock_name, stock_code, requested_indicators, xaxis_range)
        
        # 创建网格布局
        grid = Grid(init_opts=opts.InitOpts(
            width="100%",
            height=f"{dynamic_height}px",
            page_title=f"AI看线 - {stock_name}({stock_code}) {frequency_display}技术分析"
        ))
        
        # 计算子图高度和添加图表
        subplot_count = self._add_charts_to_grid(grid, overlap_kline, dates, indicators, requested_indicators, xaxis_range)
        
        # 生成HTML内容
        html_content = grid.render_embed()
        
        # 创建完整的HTML文档
        full_html = self._create_full_html(stock_name, stock_code, dates, html_content, requested_indicators, frequency_display)
        
        # 保存HTML文件到指定路径
        self._save_html_file(full_html, stock_code, requested_indicators, save_path)
        
        return full_html
    
    def _prepare_chart_data(self, stock_data):
        """准备图表数据"""
        dates = stock_data['date'].dt.strftime('%Y-%m-%d').tolist()
        k_data = [[float(stock_data['open'].iloc[i]), 
                  float(stock_data['close'].iloc[i]), 
                  float(stock_data['low'].iloc[i]), 
                  float(stock_data['high'].iloc[i])] for i in range(len(stock_data))]
        return dates, k_data
    
    def _get_stock_name(self, stock_code):
        """获取股票名称"""
        try:
            import akshare as ak
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                return stock_info.loc[stock_info['item'] == '股票简称', 'value'].values[0]
            else:
                return stock_code
        except:
            return stock_code
    
    def _get_frequency_display(self, frequency):
        """获取频率的中文显示"""
        frequency_map = {
            'daily': '日线',
            'weekly': '周线', 
            'monthly': '月线',
            '1min': '1分钟',
            '5min': '5分钟',
            '15min': '15分钟',
            '30min': '30分钟',
            '60min': '60分钟'
        }
        return frequency_map.get(frequency, '日线')
    
    def _get_frequency_display_en(self, frequency):
        """获取频率的英文显示，专门用于matplotlib图表"""
        frequency_map = {
            'daily': 'Daily',
            'weekly': 'Weekly', 
            'monthly': 'Monthly',
            '1min': '1min',
            '5min': '5min',
            '15min': '15min',
            '30min': '30min',
            '60min': '60min'
        }
        return frequency_map.get(frequency, 'Daily')
    
    def _create_kline_with_ma(self, dates, k_data, indicators, stock_name, stock_code, frequency_display=""):
        """创建带MA线的K线图"""
        # 创建K线图
        kline = Kline()
        kline.add_xaxis(dates)
        kline.add_yaxis(
            "K线",
            k_data,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            ),
        )
        
        # K线图设置
        kline.set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"{stock_name}({stock_code}) {frequency_display}K线图与成交量分析", 
                pos_left="center",
                padding=[10, 0, 0, 0],
                pos_top="1%"
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, xaxis_index=[0, 1]),
                opts.DataZoomOpts(type_="slider", range_start=0, range_end=100, xaxis_index=[0, 1]),
            ],
            legend_opts=opts.LegendOpts(
                pos_bottom="0%",
                pos_left="center",
                orient="horizontal",
                item_gap=20
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="horizontal",
                pos_right="5%",
                pos_top="top",
                feature={
                    "saveAsImage": {},
                    "dataZoom": {},
                    "dataView": {},
                    "restore": {},
                }
            ),
        )
        
        # 创建MA线
        line = Line()
        line.add_xaxis(dates)
        line.add_yaxis("MA5", indicators['MA5'].round(2).tolist(), is_smooth=True, is_symbol_show=False, 
                      linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        line.add_yaxis("MA10", indicators['MA10'].round(2).tolist(), is_smooth=True, is_symbol_show=False, 
                      linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        line.add_yaxis("MA20", indicators['MA20'].round(2).tolist(), is_smooth=True, is_symbol_show=False, 
                      linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        line.add_yaxis("MA30", indicators['MA30'].round(2).tolist(), is_smooth=True, is_symbol_show=False, 
                      linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        
        # 将线叠加到K线图上
        return kline.overlap(line)
    
    def _create_kline_with_indicators(self, dates, k_data, indicators, stock_name, stock_code, requested_indicators, xaxis_range):
        """创建带技术指标的K线图"""
        # 创建K线图
        kline = Kline()
        kline.add_xaxis(dates)
        kline.add_yaxis(
            "K线",
            k_data,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            ),
        )
        
        # 根据用户请求添加技术指标
        overlap_kline = kline
        
        # 添加MA指标
        if 'MA' in requested_indicators:
            line = Line()
            line.add_xaxis(dates)
            if 'MA5' in indicators:
                line.add_yaxis("MA5", indicators['MA5'].round(2).tolist(), 
                              is_smooth=True, is_symbol_show=False,
                              linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
            if 'MA10' in indicators:
                line.add_yaxis("MA10", indicators['MA10'].round(2).tolist(), 
                              is_smooth=True, is_symbol_show=False,
                              linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
            if 'MA20' in indicators:
                line.add_yaxis("MA20", indicators['MA20'].round(2).tolist(), 
                              is_smooth=True, is_symbol_show=False,
                              linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
            if 'MA30' in indicators:
                line.add_yaxis("MA30", indicators['MA30'].round(2).tolist(), 
                              is_smooth=True, is_symbol_show=False,
                              linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
            overlap_kline = kline.overlap(line)
        
        # 添加布林带
        if 'BOLL' in requested_indicators:
            boll_line = Line()
            boll_line.add_xaxis(dates)
            if 'BOLL_upper' in indicators:
                boll_line.add_yaxis("BOLL上轨", indicators['BOLL_upper'].round(2).tolist(), 
                                  is_smooth=True, is_symbol_show=False,
                                  linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8, type_='dashed'))
            if 'BOLL_middle' in indicators:
                boll_line.add_yaxis("BOLL中轨", indicators['BOLL_middle'].round(2).tolist(), 
                                  is_smooth=True, is_symbol_show=False,
                                  linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
            if 'BOLL_lower' in indicators:
                boll_line.add_yaxis("BOLL下轨", indicators['BOLL_lower'].round(2).tolist(), 
                                  is_smooth=True, is_symbol_show=False,
                                  linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8, type_='dashed'))
            overlap_kline = overlap_kline.overlap(boll_line)
        
        # K线图设置
        overlap_kline.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, xaxis_index=xaxis_range),
                opts.DataZoomOpts(type_="slider", range_start=0, range_end=100, xaxis_index=xaxis_range, pos_top="3%"),
            ],
            legend_opts=opts.LegendOpts(
                is_show=False  # 隐藏K线图例
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="horizontal",
                pos_right="5%",
                pos_top="top",
                feature={
                    "saveAsImage": {},
                    "dataZoom": {},
                    "dataView": {},
                    "restore": {},
                }
            ),
        )
        
        return overlap_kline
    
    def _create_volume_chart(self, dates, stock_data):
        """创建成交量图"""
        bar = Bar()
        bar.add_xaxis(dates)
        bar.add_yaxis(
            "成交量",
            stock_data['volume'].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    """
                    function(params) {
                        var colorList;
                        if (params.data >= 0) {
                            colorList = '#ef232a';
                        } else {
                            colorList = '#14b143';
                        }
                        return colorList;
                    }
                    """
                )
            ),
        )
        
        # 成交量图设置
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitline_opts=opts.SplitLineOpts(is_show=True),
                name="成交量",
                name_location="middle",
                name_gap=40,
                name_rotate=90,
            ),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, xaxis_index=[0, 1]),
            ],
            legend_opts=opts.LegendOpts(is_show=False),
        )
        
        return bar
    
    def _add_charts_to_grid(self, grid, overlap_kline, dates, indicators, requested_indicators, xaxis_range):
        """添加图表到网格布局"""
        # 计算子图高度
        subplot_count = 1  # K线图
        if 'MACD' in requested_indicators:
            subplot_count += 1
        if 'KDJ' in requested_indicators:
            subplot_count += 1
        if 'RSI' in requested_indicators:
            subplot_count += 1
        if 'BIAS' in requested_indicators:
            subplot_count += 1
        
        # 添加K线图到网格
        grid.add(overlap_kline, grid_opts=opts.GridOpts(
            pos_left="8%", 
            pos_right="5%", 
            pos_top="6%",  # 删除图例后可以上移
            height=f"{80/subplot_count}%"  # 增加高度，因为删除了图例
        ))
        
        current_top = 6 + 80/subplot_count + 5  # 调整起始位置和间距
        
        # 添加MACD图
        if 'MACD' in requested_indicators and 'MACD' in indicators:
            macd_chart = self._create_macd_chart(dates, indicators, xaxis_range)
            grid.add(macd_chart, grid_opts=opts.GridOpts(
                pos_left="8%", 
                pos_right="5%", 
                pos_top=f"{current_top}%",
                height=f"{80/subplot_count}%"
            ))
            current_top += 80/subplot_count + 5  # 增加5%的间距
        
        # 添加KDJ图
        if 'KDJ' in requested_indicators and 'K' in indicators:
            kdj_chart = self._create_kdj_chart(dates, indicators, xaxis_range)
            grid.add(kdj_chart, grid_opts=opts.GridOpts(
                pos_left="8%", 
                pos_right="5%", 
                pos_top=f"{current_top}%",
                height=f"{80/subplot_count}%"
            ))
            current_top += 80/subplot_count + 5  # 增加5%的间距
        
        # 添加RSI图
        if 'RSI' in requested_indicators and 'RSI6' in indicators:
            rsi_chart = self._create_rsi_chart(dates, indicators, xaxis_range)
            grid.add(rsi_chart, grid_opts=opts.GridOpts(
                pos_left="8%", 
                pos_right="5%", 
                pos_top=f"{current_top}%",
                height=f"{80/subplot_count}%"
            ))
            current_top += 80/subplot_count + 5  # 增加5%的间距
        
        # 添加BIAS图
        if 'BIAS' in requested_indicators and 'BIAS6' in indicators:
            bias_chart = self._create_bias_chart(dates, indicators, xaxis_range)
            grid.add(bias_chart, grid_opts=opts.GridOpts(
                pos_left="8%", 
                pos_right="5%", 
                pos_top=f"{current_top}%",
                height=f"{80/subplot_count}%"
            ))
        
        return subplot_count
    
    def _calculate_subplot_count(self, requested_indicators):
        """计算子图数量"""
        subplot_count = 1  # K线图
        if 'MACD' in requested_indicators:
            subplot_count += 1
        if 'KDJ' in requested_indicators:
            subplot_count += 1
        if 'RSI' in requested_indicators:
            subplot_count += 1
        if 'BIAS' in requested_indicators:
            subplot_count += 1
        return subplot_count
    
    def _create_macd_chart(self, dates, indicators, xaxis_range):
        """创建MACD图表"""
        macd_line = Line()
        macd_line.add_xaxis(dates)
        macd_line.add_yaxis("MACD", indicators['MACD'].round(4).tolist(), 
                           is_smooth=True, is_symbol_show=False,
                           linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        macd_line.add_yaxis("Signal", indicators['MACD_signal'].round(4).tolist(), 
                           is_smooth=True, is_symbol_show=False,
                           linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        
        # MACD柱状图
        macd_bar = Bar()
        macd_bar.add_xaxis(dates)
        macd_bar.add_yaxis(
            "MACD柱",
            indicators['MACD_hist'].round(4).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    """
                    function(params) {
                        return params.data >= 0 ? '#ef232a' : '#14b143';
                    }
                    """
                )
            ),
        )
        
        macd_chart = macd_line.overlap(macd_bar)
        macd_chart.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", is_scale=True),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, xaxis_index=xaxis_range),
            ],
            legend_opts=opts.LegendOpts(is_show=False),
        )
        
        return macd_chart
    
    def _create_kdj_chart(self, dates, indicators, xaxis_range):
        """创建KDJ图表"""
        kdj_line = Line()
        kdj_line.add_xaxis(dates)
        kdj_line.add_yaxis("K", indicators['K'].round(2).tolist(), 
                          is_smooth=True, is_symbol_show=False,
                          linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        kdj_line.add_yaxis("D", indicators['D'].round(2).tolist(), 
                          is_smooth=True, is_symbol_show=False,
                          linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        kdj_line.add_yaxis("J", indicators['J'].round(2).tolist(), 
                          is_smooth=True, is_symbol_show=False,
                          linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        
        kdj_line.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                min_=0,
                max_=100,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, xaxis_index=xaxis_range),
            ],
            legend_opts=opts.LegendOpts(is_show=False),
        )
        
        return kdj_line
    
    def _create_rsi_chart(self, dates, indicators, xaxis_range):
        """创建RSI图表"""
        rsi_line = Line()
        rsi_line.add_xaxis(dates)
        if 'RSI6' in indicators:
            rsi_line.add_yaxis("RSI6", indicators['RSI6'].round(2).tolist(), 
                              is_smooth=True, is_symbol_show=False,
                              linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        if 'RSI12' in indicators:
            rsi_line.add_yaxis("RSI12", indicators['RSI12'].round(2).tolist(), 
                              is_smooth=True, is_symbol_show=False,
                              linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        if 'RSI24' in indicators:
            rsi_line.add_yaxis("RSI24", indicators['RSI24'].round(2).tolist(), 
                              is_smooth=True, is_symbol_show=False,
                              linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        
        rsi_line.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                min_=0,
                max_=100,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, xaxis_index=xaxis_range),
            ],
            legend_opts=opts.LegendOpts(is_show=False),
        )
        
        return rsi_line
    
    def _create_bias_chart(self, dates, indicators, xaxis_range):
        """创建BIAS图表"""
        bias_line = Line()
        bias_line.add_xaxis(dates)
        if 'BIAS6' in indicators:
            bias_line.add_yaxis("BIAS6", indicators['BIAS6'].round(2).tolist(), 
                               is_smooth=True, is_symbol_show=False,
                               linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        if 'BIAS12' in indicators:
            bias_line.add_yaxis("BIAS12", indicators['BIAS12'].round(2).tolist(), 
                               is_smooth=True, is_symbol_show=False,
                               linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        if 'BIAS24' in indicators:
            bias_line.add_yaxis("BIAS24", indicators['BIAS24'].round(2).tolist(), 
                               is_smooth=True, is_symbol_show=False,
                               linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.8))
        
        bias_line.set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            datazoom_opts=[
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, xaxis_index=xaxis_range),
            ],
            legend_opts=opts.LegendOpts(is_show=False),
        )
        
        return bias_line
    
    def _create_full_html(self, stock_name, stock_code, dates, html_content, requested_indicators, frequency_display=""):
        """创建完整的HTML文档"""
        # 计算动态高度
        base_height = 500  # 增加基础高度，确保X轴完全显示
        chart_height = 350  # 增加每个图表的高度
        subplot_count = self._calculate_subplot_count(requested_indicators)
        dynamic_height = base_height + (subplot_count * chart_height)
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI看线 - {stock_name}({stock_code}) {frequency_display}技术分析</title>
    <style>
        body {{ 
            margin: 0; 
            padding: 20px; 
            font-family: "Microsoft YaHei", Arial, sans-serif; 
            background-color: #f5f5f5;
        }}
        .container {{
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        .title {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 14px;
            color: #666;
        }}
        .chart-container {{
            width: 100%;
            height: {dynamic_height}px;
        }}
        .indicators-info {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
        .indicators-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .indicators-list {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">{stock_name}({stock_code}) {frequency_display}技术分析图表</div>
            <div class="subtitle">数据时间范围: {dates[0]} 至 {dates[-1]} | 生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        <div class="chart-container">
            {html_content}
        </div>
    </div>
</body>
</html>
"""
    
    def _optimize_html_file(self, html_path):
        """优化HTML文件，添加自适应样式和脚本"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            # 添加自定义样式和Meta标签
            meta_tags = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            margin: 0; 
            padding: 0; 
            font-family: "Microsoft YaHei", Arial, sans-serif; 
        }}
        .container {{
            width: 100%;
            height: 100%;
            padding: 0;
            margin: 0;
            overflow: hidden;
        }}
        /* 标题样式优化 */
        .title-text {{
            font-size: 16px !important;
            font-weight: bold !important;
            padding: 15px 0 !important;
            margin-bottom: 15px !important;
        }}
        /* 图例样式优化 */
        .legend {{
            padding-top: 15px !important;
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
        }}
        .legend-item {{
            margin: 0 10px !important;
            display: inline-flex !important;
            align-items: center !important;
        }}
        /* 确保各种尺寸屏幕上不出现文字重叠 */
        @media (max-width: 768px) {{
            .title-text {{
                font-size: 14px !important;
            }}
            .legend-item {{
                margin: 0 5px !important;
            }}
        }}
    </style>
"""
            # 在head标签后插入
            html_content = html_content.replace('<head>', '<head>\n' + meta_tags)
            
            # 添加初始化完成后的图表调整脚本
            adjust_script = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // 在页面加载完成后执行额外的调整
            setTimeout(function() {{
                // 处理标题元素
                var titleElements = document.querySelectorAll('.title');
                titleElements.forEach(function(el) {{
                    el.classList.add('title-text');
                }});
                
                // 处理图例元素
                var legendElements = document.querySelectorAll('.legend');
                legendElements.forEach(function(el) {{
                    el.style.paddingTop = '15px';
                }});
                
                // 处理图例项
                var legendItems = document.querySelectorAll('.legend-item');
                legendItems.forEach(function(el) {{
                    el.style.margin = '0 10px';
                }});
            }}, 500);
        }});
    </script>
"""
            # 在</body>标签之前插入
            html_content = html_content.replace('</body>', adjust_script + '</body>')
            
            # 写回文件
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            print(f"修改HTML文件时出错: {e}")
    
    def _save_html_file(self, html_content, stock_code, requested_indicators, save_path):
        """保存HTML文件到指定路径"""
        try:
            # 创建保存目录
            charts_dir = os.path.join(save_path, 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            # 生成文件名：股票代码_技术指标_时间戳.html
            indicators_str = "_".join(requested_indicators)
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{stock_code}_{indicators_str}_{timestamp}.html"
            
            # 保存文件
            file_path = os.path.join(charts_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"ECharts HTML已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"保存HTML文件时出错: {e}")
            return None
    
    def create_echarts_config(self, stock_data, indicators, stock_code, requested_indicators, frequency="daily"):
        """
        创建ECharts配置的JSON格式，用于生成markdown格式的ECharts代码块
        
        参数:
            stock_data (pandas.DataFrame): 股票历史数据
            indicators (dict): 技术指标数据
            stock_code (str): 股票代码
            requested_indicators (list): 用户请求的技术指标列表
            frequency (str): 数据频率，用于显示在标题中
            
        返回:
            dict: ECharts配置字典
        """
        if stock_data.empty:
            return {
                "title": {"text": "无法获取股票数据"},
                "xAxis": {"type": "category", "data": []},
                "yAxis": {"type": "value"},
                "series": []
            }
        
        # 获取股票名称
        stock_name = self._get_stock_name(stock_code)
        frequency_display = self._get_frequency_display(frequency)
        
        # 准备基础数据
        dates, k_data = self._prepare_chart_data(stock_data)
        
        # 创建基础配置
        config = {
            "title": {
                "text": f"{stock_name}({stock_code}) {frequency_display}技术分析",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "data": ["K线"],
                "top": 30
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "data": dates,
                "scale": True,
                "boundaryGap": False,
                "axisLine": {"onZero": False},
                "splitLine": {"show": False},
                "min": "dataMin",
                "max": "dataMax"
            },
            "yAxis": {
                "scale": True,
                "splitArea": {"show": True}
            },
            "dataZoom": [
                {
                    "type": "inside",
                    "start": 0,
                    "end": 100
                },
                {
                    "show": True,
                    "type": "slider",
                    "top": "90%",
                    "start": 0,
                    "end": 100
                }
            ],
            "series": []
        }
        
        # 添加K线图
        kline_series = {
            "name": "K线",
            "type": "candlestick",
            "data": k_data,
            "itemStyle": {
                "color": "#ec0000",
                "color0": "#00da3c",
                "borderColor": "#8A0000",
                "borderColor0": "#008F28"
            }
        }
        config["series"].append(kline_series)
        
        # 添加技术指标
        legend_data = ["K线"]
        
        # 添加移动平均线 (MA)
        if "MA" in requested_indicators:
            if "MA5" in indicators:
                ma5_data = [float(x) if not pd.isna(x) else 0 for x in indicators["MA5"]]
                config["series"].append({
                    "name": "MA5",
                    "type": "line",
                    "data": ma5_data,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#FF6B6B"}
                })
                legend_data.append("MA5")
            
            if "MA10" in indicators:
                ma10_data = [float(x) if not pd.isna(x) else 0 for x in indicators["MA10"]]
                config["series"].append({
                    "name": "MA10", 
                    "type": "line",
                    "data": ma10_data,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#4ECDC4"}
                })
                legend_data.append("MA10")
                
            if "MA20" in indicators:
                ma20_data = [float(x) if not pd.isna(x) else 0 for x in indicators["MA20"]]
                config["series"].append({
                    "name": "MA20",
                    "type": "line", 
                    "data": ma20_data,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#45B7D1"}
                })
                legend_data.append("MA20")
        
        # 添加布林带 (BOLL)
        if "BOLL" in requested_indicators:
            if "BOLL_upper" in indicators:
                boll_upper = [float(x) if not pd.isna(x) else 0 for x in indicators["BOLL_upper"]]
                config["series"].append({
                    "name": "BOLL上轨",
                    "type": "line",
                    "data": boll_upper,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#FFA500"}
                })
                legend_data.append("BOLL上轨")
                
            if "BOLL_middle" in indicators:
                boll_middle = [float(x) if not pd.isna(x) else 0 for x in indicators["BOLL_middle"]]
                config["series"].append({
                    "name": "BOLL中轨",
                    "type": "line",
                    "data": boll_middle,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#32CD32"}
                })
                legend_data.append("BOLL中轨")
                
            if "BOLL_lower" in indicators:
                boll_lower = [float(x) if not pd.isna(x) else 0 for x in indicators["BOLL_lower"]]
                config["series"].append({
                    "name": "BOLL下轨",
                    "type": "line",
                    "data": boll_lower,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#FF6347"}
                })
                legend_data.append("BOLL下轨")
        
        # 添加MACD指标
        if "MACD" in requested_indicators:
            if "MACD" in indicators:
                macd_data = [float(x) if not pd.isna(x) else 0 for x in indicators["MACD"]]
                config["series"].append({
                    "name": "MACD",
                    "type": "line",
                    "data": macd_data,
                    "smooth": True,
                    "lineStyle": {"width": 2, "color": "#FF0000"}
                })
                legend_data.append("MACD")
            
            if "MACD_signal" in indicators:
                macd_signal_data = [float(x) if not pd.isna(x) else 0 for x in indicators["MACD_signal"]]
                config["series"].append({
                    "name": "MACD信号线",
                    "type": "line",
                    "data": macd_signal_data,
                    "smooth": True,
                    "lineStyle": {"width": 2, "color": "#00FF00"}
                })
                legend_data.append("MACD信号线")
            
            if "MACD_hist" in indicators:
                macd_hist_data = [float(x) if not pd.isna(x) else 0 for x in indicators["MACD_hist"]]
                config["series"].append({
                    "name": "MACD柱状图",
                    "type": "bar",
                    "data": macd_hist_data,
                    "itemStyle": {
                        "color": "#0000FF"
                    }
                })
                legend_data.append("MACD柱状图")
        
        # 添加KDJ指标
        if "KDJ" in requested_indicators:
            if "K" in indicators:
                k_data = [float(x) if not pd.isna(x) else 0 for x in indicators["K"]]
                config["series"].append({
                    "name": "KDJ-K",
                    "type": "line",
                    "data": k_data,
                    "smooth": True,
                    "lineStyle": {"width": 2, "color": "#FF1493"}
                })
                legend_data.append("KDJ-K")
            
            if "D" in indicators:
                d_data = [float(x) if not pd.isna(x) else 0 for x in indicators["D"]]
                config["series"].append({
                    "name": "D线",
                    "type": "line",
                    "data": d_data,
                    "smooth": True,
                    "lineStyle": {"width": 2, "color": "#00CED1"}
                })
                legend_data.append("D线")
            
            if "J" in indicators:
                j_data = [float(x) if not pd.isna(x) else 0 for x in indicators["J"]]
                config["series"].append({
                    "name": "J线",
                    "type": "line",
                    "data": j_data,
                    "smooth": True,
                    "lineStyle": {"width": 2, "color": "#FFD700"}
                })
                legend_data.append("J线")
        
        # 添加BIAS指标
        if "BIAS" in requested_indicators:
            if "BIAS6" in indicators:
                bias6_data = [float(x) if not pd.isna(x) else 0 for x in indicators["BIAS6"]]
                config["series"].append({
                    "name": "BIAS6",
                    "type": "line",
                    "data": bias6_data,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#8A2BE2"}
                })
                legend_data.append("BIAS6")
            
            if "BIAS12" in indicators:
                bias12_data = [float(x) if not pd.isna(x) else 0 for x in indicators["BIAS12"]]
                config["series"].append({
                    "name": "BIAS12",
                    "type": "line",
                    "data": bias12_data,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#DC143C"}
                })
                legend_data.append("BIAS12")
            
            if "BIAS24" in indicators:
                bias24_data = [float(x) if not pd.isna(x) else 0 for x in indicators["BIAS24"]]
                config["series"].append({
                    "name": "BIAS24",
                    "type": "line",
                    "data": bias24_data,
                    "smooth": True,
                    "lineStyle": {"width": 1, "color": "#B22222"}
                })
                legend_data.append("BIAS24")
        
        # 更新图例数据
        config["legend"]["data"] = legend_data
        
        return config