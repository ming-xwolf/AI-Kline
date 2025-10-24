import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import seaborn as sns
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# 设置字体 - 使用系统默认字体
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

class ChanVisualizer:
    """
    缠论可视化类，负责创建缠论分析的各种图表
    """
    
    def __init__(self):
        self.colors = {
            'up_pen': '#FF4444',
            'down_pen': '#00AA00', 
            'up_segment': '#FF6666',
            'down_segment': '#00CC00',
            'zhongshu': '#4444FF',
            'trend_up': '#FF0000',
            'trend_down': '#00FF00',
            'signal_buy': '#FFD700',
            'signal_sell': '#FF6B6B'
        }
    
    def create_comprehensive_chan_chart(self, stock_data: pd.DataFrame, 
                                      analysis_result: Dict, 
                                      save_path: str = None) -> str:
        """
        创建综合缠论分析图表
        
        参数:
            stock_data: 股票数据
            analysis_result: 缠论分析结果
            save_path: 保存路径
            
        返回:
            str: 图表文件路径
        """
        # 创建子图布局
        fig = plt.figure(figsize=(20, 16))
        
        # 主图：K线 + 缠论分析
        ax_main = plt.subplot2grid((4, 4), (0, 0), colspan=4, rowspan=3)
        
        # 成交量图
        ax_volume = plt.subplot2grid((4, 4), (3, 0), colspan=4, rowspan=1)
        
        # 绘制主图
        self._plot_chan_main_chart(ax_main, stock_data, analysis_result)
        
        # 绘制成交量
        self._plot_volume_chart(ax_volume, stock_data)
        
        # 添加分析摘要
        self._add_analysis_summary(fig, analysis_result)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def _plot_chan_main_chart(self, ax, stock_data: pd.DataFrame, analysis_result: Dict):
        """绘制缠论主图"""
        dates = pd.to_datetime(stock_data['date'])
        
        # 绘制K线
        self._plot_candlestick(ax, stock_data, dates)
        
        # 从正确的数据结构中获取数据
        basic_analysis = analysis_result.get('basic_analysis', {})
        pen_data = basic_analysis.get('pen_data', [])
        segment_data = basic_analysis.get('segment_data', [])
        zhongshu_data = basic_analysis.get('zhongshu_data', [])
        signals = basic_analysis.get('signals', [])
        
        # 绘制笔
        self._plot_pens(ax, pen_data)
        
        # 绘制线段
        self._plot_segments(ax, segment_data)
        
        # 绘制中枢
        self._plot_zhongshu(ax, zhongshu_data)
        
        # 绘制交易信号
        self._plot_signals(ax, signals, stock_data)
        
        # 设置图表属性
        ax.set_title('Chan Theory Analysis - Pens, Segments, Central Pivots', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 设置X轴日期格式
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=2))
        
        # 添加自定义图例
        self._add_custom_legend(ax)
        
        # 旋转x轴标签
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _add_custom_legend(self, ax):
        """添加自定义图例"""
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        
        # 创建图例元素
        legend_elements = [
            # K线图例
            Patch(facecolor='red', alpha=0.7, edgecolor='black', label='Bullish Candle'),
            Patch(facecolor='green', alpha=0.7, edgecolor='black', label='Bearish Candle'),
            
            # 笔的图例
            Line2D([0], [0], color=self.colors['up_pen'], linewidth=3, alpha=0.8, label='Up Pen'),
            Line2D([0], [0], color=self.colors['down_pen'], linewidth=3, alpha=0.8, label='Down Pen'),
            
            # 线段的图例
            Line2D([0], [0], color=self.colors['up_segment'], linewidth=5, alpha=0.6, 
                   linestyle='--', label='Up Segment'),
            Line2D([0], [0], color=self.colors['down_segment'], linewidth=5, alpha=0.6, 
                   linestyle='--', label='Down Segment'),
            
            # 中枢的图例
            Patch(facecolor=self.colors['zhongshu'], alpha=0.2, edgecolor=self.colors['zhongshu'], 
                  linewidth=2, label='Central Pivot'),
            
            # 交易信号的图例
            Line2D([0], [0], marker='^', color=self.colors['signal_buy'], markersize=8, 
                   linestyle='None', label='Buy Signal'),
            Line2D([0], [0], marker='v', color=self.colors['signal_sell'], markersize=8, 
                   linestyle='None', label='Sell Signal')
        ]
        
        # 添加图例到图表
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9, 
                framealpha=0.9, fancybox=True, shadow=True)
    
    def _plot_candlestick(self, ax, stock_data: pd.DataFrame, dates):
        """绘制K线图"""
        for i, (date, row) in enumerate(zip(dates, stock_data.itertuples())):
            color = 'red' if row.close >= row.open else 'green'
            
            # 绘制实体 - 使用实际日期而不是索引
            height = abs(row.close - row.open)
            bottom = min(row.open, row.close)
            width = pd.Timedelta(days=0.8)  # 使用时间宽度
            rect = Rectangle((date - width/2, bottom), width, height, 
                          facecolor=color, alpha=0.7, edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
            # 绘制影线 - 使用实际日期
            ax.plot([date, date], [row.low, row.high], color='black', linewidth=1)
    
    def _plot_pens(self, ax, pen_data: List[Dict]):
        """绘制笔"""
        for i, pen in enumerate(pen_data):
            start_date = pd.to_datetime(pen['start_date'])
            end_date = pd.to_datetime(pen['end_date'])
            start_price = pen['start_price']
            end_price = pen['end_price']
            
            color = self.colors['up_pen'] if pen['direction'] == 'up' else self.colors['down_pen']
            
            # 绘制笔线
            ax.plot([start_date, end_date], [start_price, end_price], 
                   color=color, linewidth=3, alpha=0.8, 
                   label='Pen' if i == 0 else "")
            
            # 标记笔的端点
            ax.scatter([start_date, end_date], [start_price, end_price], 
                      color=color, s=80, zorder=5, marker='o')
            
            # 添加笔的标签
            mid_date = start_date + (end_date - start_date) / 2
            mid_price = (start_price + end_price) / 2
            ax.text(mid_date, mid_price, f'P{i+1}', 
                   ha='center', va='center', fontsize=8, 
                   bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.3))
    
    def _plot_segments(self, ax, segment_data: List[Dict]):
        """绘制线段"""
        for i, segment in enumerate(segment_data):
            start_date = pd.to_datetime(segment['start_date'])
            end_date = pd.to_datetime(segment['end_date'])
            start_price = segment['start_price']
            end_price = segment['end_price']
            
            color = self.colors['up_segment'] if segment['direction'] == 'up' else self.colors['down_segment']
            
            # 绘制线段
            ax.plot([start_date, end_date], [start_price, end_price], 
                   color=color, linewidth=5, alpha=0.6, linestyle='--',
                   label='Segment' if i == 0 else "")
            
            # 标记线段端点
            ax.scatter([start_date, end_date], [start_price, end_price], 
                      color=color, s=100, zorder=6, marker='s')
            
            # 添加线段标签
            mid_date = start_date + (end_date - start_date) / 2
            mid_price = (start_price + end_price) / 2
            ax.text(mid_date, mid_price, f'S{i+1}', 
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.5))
    
    def _plot_zhongshu(self, ax, zhongshu_data: List[Dict]):
        """绘制中枢"""
        for i, zs in enumerate(zhongshu_data):
            start_date = pd.to_datetime(zs['start_date'])
            end_date = pd.to_datetime(zs['end_date'])
            
            # 绘制中枢区域（使用填充区域而不是矩形）
            ax.fill_between([start_date, end_date], 
                           [zs['low'], zs['low']], 
                           [zs['high'], zs['high']],
                           color=self.colors['zhongshu'], alpha=0.2,
                           label='Central Pivot' if i == 0 else "")
            
            # 标记中枢中心
            center_date = start_date + (end_date - start_date) / 2
            ax.text(center_date, zs['center'], f'CP{i+1}\nStr:{zs["strength"]:.2f}', 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.4", facecolor='yellow', alpha=0.8))
            
            # 绘制中枢边界线
            ax.axhline(y=zs['high'], color=self.colors['zhongshu'], 
                      linestyle=':', alpha=0.7, linewidth=2)
            ax.axhline(y=zs['low'], color=self.colors['zhongshu'], 
                      linestyle=':', alpha=0.7, linewidth=2)
    
    def _plot_signals(self, ax, signals: List[Dict], stock_data: pd.DataFrame):
        """绘制交易信号"""
        for signal in signals:
            if signal['type'] == 'breakout':
                # 在最新价格位置标记突破信号
                latest_date = pd.to_datetime(stock_data['date'].iloc[-1])
                latest_price = stock_data['close'].iloc[-1]
                
                color = self.colors['signal_buy'] if signal['direction'] == 'up' else self.colors['signal_sell']
                marker = '^' if signal['direction'] == 'up' else 'v'
                
                ax.scatter(latest_date, latest_price, 
                          color=color, s=200, marker=marker, zorder=10,
                          label=f"Breakout({signal['strength']})" if signal == signals[0] else "")
                
                ax.annotate(f"Breakout\nStr:{signal['strength']}", 
                           xy=(latest_date, latest_price),
                           xytext=(10, 20), textcoords='offset points',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor=color, alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    def _plot_volume_chart(self, ax, stock_data: pd.DataFrame):
        """绘制成交量图"""
        dates = pd.to_datetime(stock_data['date'])
        volumes = stock_data['volume']
        
        # 绘制成交量柱状图
        colors = ['red' if stock_data.iloc[i]['close'] >= stock_data.iloc[i]['open'] 
                 else 'green' for i in range(len(stock_data))]
        
        ax.bar(dates, volumes, color=colors, alpha=0.7, width=0.8)
        ax.set_title('Volume Analysis', fontsize=14, fontweight='bold')
        ax.set_ylabel('Volume', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 添加成交量移动平均线
        if len(volumes) >= 5:
            volume_ma5 = volumes.rolling(window=5).mean()
            ax.plot(dates, volume_ma5, color='blue', linewidth=2, alpha=0.8, label='Volume MA5')
            ax.legend()
        
        # 旋转x轴标签
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _add_analysis_summary(self, fig, analysis_result: Dict):
        """添加分析摘要"""
        # 从正确的数据结构中获取数据
        basic_analysis = analysis_result.get('basic_analysis', {})
        result = basic_analysis.get('analysis_result', {})
        
        # 获取实际的数据
        pen_data = basic_analysis.get('pen_data', [])
        segment_data = basic_analysis.get('segment_data', [])
        zhongshu_data = basic_analysis.get('zhongshu_data', [])
        signals = basic_analysis.get('signals', [])
        
        # 获取并转换中文值为英文
        risk_level = result.get('risk_level', 'Unknown')
        recommendation = result.get('recommendation', 'Watch')
        trend_analysis = result.get('trend_analysis', 'No Data')
        
        # 转换中文值为英文
        risk_translation = {
            '低风险': 'Low Risk',
            '中风险': 'Medium Risk', 
            '高风险': 'High Risk',
            '未知': 'Unknown',
            '低': 'Low Risk',
            '中': 'Medium Risk',
            '高': 'High Risk'
        }
        
        recommendation_translation = {
            '建议买入': 'Buy',
            '建议卖出': 'Sell',
            '建议观望': 'Watch',
            '观望': 'Watch',
            '买入': 'Buy',
            '卖出': 'Sell'
        }
        
        trend_translation = {
            '上涨趋势': 'Uptrend',
            '下跌趋势': 'Downtrend',
            '震荡趋势': 'Sideways',
            '无数据': 'No Data',
            'trending': 'Trending',
            'up': 'Up',
            'down': 'Down'
        }
        
        # 应用翻译
        risk_level_en = risk_translation.get(risk_level, risk_level)
        recommendation_en = recommendation_translation.get(recommendation, recommendation)
        
        # 解析趋势分析字符串
        trend_analysis_en = "No Data"
        if trend_analysis and trend_analysis != "No Data":
            # 解析类似 "趋势类型: trending, 方向: up, 强度: 0.13" 的字符串
            try:
                if "趋势类型:" in trend_analysis and "方向:" in trend_analysis and "强度:" in trend_analysis:
                    # 提取各个部分
                    parts = trend_analysis.split(", ")
                    trend_type = "Unknown"
                    direction = "Unknown"
                    strength = "0.00"
                    
                    for part in parts:
                        if "趋势类型:" in part:
                            trend_type = part.split(":")[1].strip()
                        elif "方向:" in part:
                            direction = part.split(":")[1].strip()
                        elif "强度:" in part:
                            strength = part.split(":")[1].strip()
                    
                    # 翻译并格式化
                    trend_type_en = trend_translation.get(trend_type, trend_type)
                    direction_en = trend_translation.get(direction, direction)
                    trend_analysis_en = f"{trend_type_en}, {direction_en}, {strength}"
                else:
                    trend_analysis_en = trend_translation.get(trend_analysis, trend_analysis)
            except:
                trend_analysis_en = "No Data"
        
        # 创建摘要文本
        summary_text = f"""
Chan Analysis Summary:
• Pens: {len(pen_data)}
• Segments: {len(segment_data)}  
• Central Pivots: {len(zhongshu_data)}
• Signals: {len(signals)}
• Risk Level: {risk_level_en}
• Recommendation: {recommendation_en}
• Trend: {trend_analysis_en}
        """
        
        # 在图表上添加文本
        fig.text(0.02, 0.98, summary_text, transform=fig.transFigure, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    def create_interactive_chan_chart(self, stock_data: pd.DataFrame, 
                                    analysis_result: Dict, 
                                    save_path: str = None) -> str:
        """
        创建交互式缠论分析图表（使用Plotly）
        
        参数:
            stock_data: 股票数据
            analysis_result: 缠论分析结果
            save_path: 保存路径
            
        返回:
            str: HTML文件路径
        """
        # 创建子图
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Chan Theory Analysis', 'Volume'),
            row_heights=[0.7, 0.3]
        )
        
        # 绘制主图
        self._plot_interactive_main(fig, stock_data, analysis_result)
        
        # 绘制成交量
        self._plot_interactive_volume(fig, stock_data)
        
        # 更新布局
        fig.update_layout(
            title='缠论技术分析图',
            xaxis_title='日期',
            yaxis_title='价格',
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        # 保存或显示
        if save_path:
            fig.write_html(save_path)
            return save_path
        else:
            fig.show()
            return ""
    
    def _plot_interactive_main(self, fig, stock_data: pd.DataFrame, analysis_result: Dict):
        """绘制交互式主图"""
        dates = pd.to_datetime(stock_data['date'])
        
        # 绘制K线
        fig.add_trace(go.Candlestick(
            x=dates,
            open=stock_data['open'],
            high=stock_data['high'],
            low=stock_data['low'],
            close=stock_data['close'],
            name='K线',
            increasing_line_color='red',
            decreasing_line_color='green'
        ), row=1, col=1)
        
        # 绘制笔
        pen_data = analysis_result.get('pen_data', [])
        for i, pen in enumerate(pen_data):
            start_date = pd.to_datetime(pen['start_date'])
            end_date = pd.to_datetime(pen['end_date'])
            
            fig.add_trace(go.Scatter(
                x=[start_date, end_date],
                y=[pen['start_price'], pen['end_price']],
                mode='lines+markers',
                name=f'笔{i+1}',
                line=dict(color=self.colors['up_pen'] if pen['direction'] == 'up' else self.colors['down_pen'], 
                         width=3),
                marker=dict(size=8)
            ), row=1, col=1)
        
        # 绘制中枢
        zhongshu_data = analysis_result.get('zhongshu_data', [])
        for i, zs in enumerate(zhongshu_data):
            start_date = pd.to_datetime(zs['start_date'])
            end_date = pd.to_datetime(zs['end_date'])
            
            # 添加中枢矩形
            fig.add_shape(
                type="rect",
                x0=start_date, y0=zs['low'],
                x1=end_date, y1=zs['high'],
                fillcolor=self.colors['zhongshu'],
                opacity=0.2,
                line=dict(color=self.colors['zhongshu'], width=2),
                row=1, col=1
            )
            
            # 添加中枢标签
            center_date = start_date + (end_date - start_date) / 2
            fig.add_annotation(
                x=center_date,
                y=zs['center'],
                text=f"中枢{i+1}<br>强度:{zs['strength']:.2f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=self.colors['zhongshu'],
                row=1, col=1
            )
    
    def _plot_interactive_volume(self, fig, stock_data: pd.DataFrame):
        """绘制交互式成交量"""
        dates = pd.to_datetime(stock_data['date'])
        volumes = stock_data['volume']
        
        # 根据涨跌设置颜色
        colors = ['red' if stock_data.iloc[i]['close'] >= stock_data.iloc[i]['open'] 
                 else 'green' for i in range(len(stock_data))]
        
        fig.add_trace(go.Bar(
            x=dates,
            y=volumes,
            name='成交量',
            marker_color=colors,
            opacity=0.7
        ), row=2, col=1)
        
        # 添加成交量移动平均线
        if len(volumes) >= 5:
            volume_ma5 = volumes.rolling(window=5).mean()
            fig.add_trace(go.Scatter(
                x=dates,
                y=volume_ma5,
                mode='lines',
                name='成交量MA5',
                line=dict(color='blue', width=2)
            ), row=2, col=1)
    
    def create_chan_analysis_report(self, analysis_result: Dict, stock_code: str) -> str:
        """
        创建缠论分析报告
        
        参数:
            analysis_result: 缠论分析结果
            stock_code: 股票代码
            
        返回:
            str: 分析报告文本
        """
        basic_analysis = analysis_result.get('basic_analysis', {})
        result = basic_analysis.get('analysis_result', {})
        pen_data = basic_analysis.get('pen_data', [])
        segment_data = basic_analysis.get('segment_data', [])
        zhongshu_data = basic_analysis.get('zhongshu_data', [])
        signals = basic_analysis.get('signals', [])
        
        report = f"""
# {stock_code} 缠论技术分析报告

## 分析概览
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **笔数量**: {result.get('pen_count', 0)}
- **线段数量**: {result.get('segment_count', 0)}
- **中枢数量**: {result.get('zhongshu_count', 0)}
- **交易信号**: {result.get('signal_count', 0)}个
- **风险等级**: {result.get('risk_level', '未知')}

## 笔分析
"""
        
        if pen_data:
            report += f"- 共识别出 {len(pen_data)} 个笔\n"
            for i, pen in enumerate(pen_data[-5:]):  # 显示最近5个笔
                report += f"  - 笔{i+1}: {pen['start_date']} 到 {pen['end_date']}, 方向: {pen['direction']}, 长度: {pen['length']}天\n"
        else:
            report += "- 未识别出有效的笔\n"
        
        report += "\n## 线段分析\n"
        if segment_data:
            report += f"- 共识别出 {len(segment_data)} 个线段\n"
            for i, segment in enumerate(segment_data[-3:]):  # 显示最近3个线段
                report += f"  - 线段{i+1}: {segment['start_date']} 到 {segment['end_date']}, 方向: {segment['direction']}\n"
        else:
            report += "- 未识别出有效的线段\n"
        
        report += "\n## 中枢分析\n"
        if zhongshu_data:
            report += f"- 共识别出 {len(zhongshu_data)} 个中枢\n"
            for i, zs in enumerate(zhongshu_data):
                report += f"  - 中枢{i+1}: {zs['start_date']} 到 {zs['end_date']}\n"
                report += f"    价格区间: {zs['low']:.2f} - {zs['high']:.2f}\n"
                report += f"    中心价格: {zs['center']:.2f}\n"
                report += f"    强度: {zs['strength']:.2f}\n"
        else:
            report += "- 未识别出有效的中枢\n"
        
        report += "\n## 交易信号\n"
        if signals:
            for i, signal in enumerate(signals):
                report += f"- 信号{i+1}: {signal['type']}, 方向: {signal['direction']}, 强度: {signal['strength']}, 置信度: {signal['confidence']:.2f}\n"
        else:
            report += "- 当前无交易信号\n"
        
        report += f"\n## 投资建议\n"
        report += f"- **建议**: {result.get('recommendation', '观望')}\n"
        report += f"- **趋势分析**: {result.get('trend_analysis', '无数据')}\n"
        
        report += "\n## 风险提示\n"
        report += "- 本分析基于缠论理论，仅供参考\n"
        report += "- 投资有风险，入市需谨慎\n"
        report += "- 请结合基本面分析和其他技术指标综合判断\n"
        
        return report
