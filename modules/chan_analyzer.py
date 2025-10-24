import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ChanAnalyzer:
    """
    缠论分析类，实现缠论理论的核心算法
    包括笔、线段、中枢的识别和分析
    """
    
    def __init__(self):
        self.pen_data = []  # 笔数据
        self.segment_data = []  # 线段数据
        self.zhongshu_data = []  # 中枢数据
        self.trend_data = []  # 趋势数据
        
    def analyze(self, stock_data: pd.DataFrame) -> Dict:
        """
        执行完整的缠论分析
        
        参数:
            stock_data: 股票数据，包含OHLCV
            
        返回:
            dict: 包含所有分析结果的字典
        """
        if stock_data.empty:
            return {}
            
        # 确保数据按时间排序
        stock_data = stock_data.sort_values('date').reset_index(drop=True)
        
        # 1. 识别笔
        self.pen_data = self._identify_pens(stock_data)
        
        # 2. 识别线段
        self.segment_data = self._identify_segments(self.pen_data)
        
        # 3. 识别中枢
        self.zhongshu_data = self._identify_zhongshu(self.segment_data)
        
        # 4. 分析趋势
        self.trend_data = self._analyze_trend(self.segment_data, self.zhongshu_data)
        
        # 5. 生成交易信号
        signals = self._generate_signals()
        
        # 6. 计算分析结果
        analysis_result = self._calculate_analysis_result()
        
        return {
            'pen_data': self.pen_data,
            'segment_data': self.segment_data,
            'zhongshu_data': self.zhongshu_data,
            'trend_data': self.trend_data,
            'signals': signals,
            'analysis_result': analysis_result
        }
    
    def _identify_pens(self, data: pd.DataFrame) -> List[Dict]:
        """
        识别笔
        
        笔的定义：
        1. 至少包含3个K线
        2. 笔的方向由起始点和结束点决定
        3. 笔内不能有包含关系
        """
        pens = []
        if len(data) < 3:
            return pens
            
        # 获取高低点
        highs = data['high'].values
        lows = data['low'].values
        dates = data['date'].values
        
        i = 0
        while i < len(data) - 2:
            # 寻找分型点
            pen_start = self._find_fenxing_start(data, i)
            if pen_start == -1:
                break
                
            pen_end = self._find_fenxing_end(data, pen_start)
            if pen_end == -1:
                break
                
            # 创建笔
            pen = {
                'start_index': pen_start,
                'end_index': pen_end,
                'start_date': dates[pen_start],
                'end_date': dates[pen_end],
                'start_price': highs[pen_start] if self._is_top_fenxing(data, pen_start) else lows[pen_start],
                'end_price': highs[pen_end] if self._is_top_fenxing(data, pen_end) else lows[pen_end],
                'direction': 'up' if self._is_up_pen(data, pen_start, pen_end) else 'down',
                'length': pen_end - pen_start + 1
            }
            
            pens.append(pen)
            i = pen_end + 1
            
        return pens
    
    def _find_fenxing_start(self, data: pd.DataFrame, start_idx: int) -> int:
        """寻找分型起始点"""
        for i in range(start_idx, len(data) - 2):
            if self._is_fenxing(data, i):
                return i
        return -1
    
    def _find_fenxing_end(self, data: pd.DataFrame, start_idx: int) -> int:
        """寻找分型结束点"""
        start_direction = 'up' if self._is_top_fenxing(data, start_idx) else 'down'
        
        for i in range(start_idx + 2, len(data) - 2):
            if self._is_fenxing(data, i):
                current_direction = 'up' if self._is_top_fenxing(data, i) else 'down'
                if current_direction != start_direction:
                    return i
        return -1
    
    def _is_fenxing(self, data: pd.DataFrame, idx: int) -> bool:
        """判断是否为分型点"""
        if idx < 1 or idx >= len(data) - 1:
            return False
            
        # 顶分型：中间高，两边低
        if (data.iloc[idx]['high'] > data.iloc[idx-1]['high'] and 
            data.iloc[idx]['high'] > data.iloc[idx+1]['high']):
            return True
            
        # 底分型：中间低，两边高
        if (data.iloc[idx]['low'] < data.iloc[idx-1]['low'] and 
            data.iloc[idx]['low'] < data.iloc[idx+1]['low']):
            return True
            
        return False
    
    def _is_top_fenxing(self, data: pd.DataFrame, idx: int) -> bool:
        """判断是否为顶分型"""
        if idx < 1 or idx >= len(data) - 1:
            return False
        return (data.iloc[idx]['high'] > data.iloc[idx-1]['high'] and 
                data.iloc[idx]['high'] > data.iloc[idx+1]['high'])
    
    def _is_up_pen(self, data: pd.DataFrame, start_idx: int, end_idx: int) -> bool:
        """判断笔的方向"""
        start_price = data.iloc[start_idx]['low'] if self._is_top_fenxing(data, start_idx) else data.iloc[start_idx]['low']
        end_price = data.iloc[end_idx]['high'] if self._is_top_fenxing(data, end_idx) else data.iloc[end_idx]['high']
        return end_price > start_price
    
    def _identify_segments(self, pens: List[Dict]) -> List[Dict]:
        """
        识别线段
        
        线段的定义：
        1. 由笔组成
        2. 线段内不能有包含关系
        3. 线段有明确的方向
        """
        segments = []
        if len(pens) < 2:
            return segments
            
        i = 0
        while i < len(pens) - 1:
            segment_start = i
            segment_end = self._find_segment_end(pens, i)
            
            if segment_end > segment_start:
                segment = {
                    'start_pen': segment_start,
                    'end_pen': segment_end,
                    'start_date': pens[segment_start]['start_date'],
                    'end_date': pens[segment_end]['end_date'],
                    'start_price': pens[segment_start]['start_price'],
                    'end_price': pens[segment_end]['end_price'],
                    'direction': self._get_segment_direction(pens, segment_start, segment_end),
                    'length': segment_end - segment_start + 1
                }
                segments.append(segment)
                i = segment_end + 1
            else:
                i += 1
                
        return segments
    
    def _find_segment_end(self, pens: List[Dict], start_idx: int) -> int:
        """寻找线段结束点"""
        if start_idx >= len(pens) - 1:
            return start_idx
            
        start_direction = pens[start_idx]['direction']
        
        for i in range(start_idx + 1, len(pens)):
            if pens[i]['direction'] != start_direction:
                return i - 1
                
        return len(pens) - 1
    
    def _get_segment_direction(self, pens: List[Dict], start_idx: int, end_idx: int) -> str:
        """获取线段方向"""
        start_price = pens[start_idx]['start_price']
        end_price = pens[end_idx]['end_price']
        return 'up' if end_price > start_price else 'down'
    
    def _identify_zhongshu(self, segments: List[Dict]) -> List[Dict]:
        """
        识别中枢
        
        中枢的定义：
        1. 由至少3个线段组成
        2. 前3个线段必须有重叠
        3. 中枢有明确的高低点
        """
        zhongshu_list = []
        if len(segments) < 3:
            return zhongshu_list
            
        i = 0
        while i < len(segments) - 2:
            # 检查前3个线段是否有重叠
            if self._has_overlap(segments[i:i+3]):
                zhongshu = self._create_zhongshu(segments, i)
                if zhongshu:
                    zhongshu_list.append(zhongshu)
                    i += 3
                else:
                    i += 1
            else:
                i += 1
                
        return zhongshu_list
    
    def _has_overlap(self, segments: List[Dict]) -> bool:
        """检查线段是否有重叠"""
        if len(segments) < 3:
            return False
            
        # 获取价格区间
        prices = []
        for seg in segments:
            prices.extend([seg['start_price'], seg['end_price']])
            
        # 检查是否有重叠
        min_price = min(prices)
        max_price = max(prices)
        
        # 简单重叠检查：如果价格区间有交集
        return max_price - min_price < sum(abs(seg['end_price'] - seg['start_price']) for seg in segments)
    
    def _create_zhongshu(self, segments: List[Dict], start_idx: int) -> Optional[Dict]:
        """创建中枢"""
        if start_idx + 2 >= len(segments):
            return None
            
        seg_group = segments[start_idx:start_idx+3]
        
        # 计算中枢的高低点
        all_prices = []
        for seg in seg_group:
            all_prices.extend([seg['start_price'], seg['end_price']])
            
        zhongshu_high = max(all_prices)
        zhongshu_low = min(all_prices)
        
        return {
            'start_segment': start_idx,
            'end_segment': start_idx + 2,
            'start_date': seg_group[0]['start_date'],
            'end_date': seg_group[-1]['end_date'],
            'high': zhongshu_high,
            'low': zhongshu_low,
            'center': (zhongshu_high + zhongshu_low) / 2,
            'range': zhongshu_high - zhongshu_low,
            'strength': self._calculate_zhongshu_strength(seg_group)
        }
    
    def _calculate_zhongshu_strength(self, segments: List[Dict]) -> float:
        """计算中枢强度"""
        if not segments:
            return 0.0
            
        # 基于线段长度和价格变化计算强度
        total_length = sum(seg['length'] for seg in segments)
        price_change = abs(segments[-1]['end_price'] - segments[0]['start_price'])
        
        return min(1.0, (total_length * price_change) / 100)
    
    def _analyze_trend(self, segments: List[Dict], zhongshu_list: List[Dict]) -> List[Dict]:
        """分析趋势"""
        trends = []
        if not segments:
            return trends
            
        # 基于线段和中枢分析趋势
        current_trend = {
            'type': 'unknown',
            'strength': 0.0,
            'direction': 'unknown',
            'start_date': segments[0]['start_date'] if segments else None,
            'end_date': segments[-1]['end_date'] if segments else None
        }
        
        # 分析趋势类型
        if len(zhongshu_list) > 0:
            current_trend['type'] = 'trending'
            current_trend['strength'] = sum(zs['strength'] for zs in zhongshu_list) / len(zhongshu_list)
        else:
            current_trend['type'] = 'sideways'
            current_trend['strength'] = 0.5
            
        # 分析趋势方向
        if segments:
            first_seg = segments[0]
            last_seg = segments[-1]
            if last_seg['end_price'] > first_seg['start_price']:
                current_trend['direction'] = 'up'
            else:
                current_trend['direction'] = 'down'
                
        trends.append(current_trend)
        return trends
    
    def _generate_signals(self) -> List[Dict]:
        """生成交易信号"""
        signals = []
        
        if not self.segment_data or not self.zhongshu_data:
            return signals
            
        # 基于缠论理论生成信号
        latest_segment = self.segment_data[-1] if self.segment_data else None
        latest_zhongshu = self.zhongshu_data[-1] if self.zhongshu_data else None
        
        if latest_segment and latest_zhongshu:
            # 突破信号
            if self._is_breakout(latest_segment, latest_zhongshu):
                signals.append({
                    'type': 'breakout',
                    'direction': latest_segment['direction'],
                    'strength': 'strong' if latest_segment['end_price'] > latest_zhongshu['high'] else 'weak',
                    'confidence': 0.8
                })
            
            # 回调信号
            if self._is_pullback(latest_segment, latest_zhongshu):
                signals.append({
                    'type': 'pullback',
                    'direction': 'opposite',
                    'strength': 'medium',
                    'confidence': 0.6
                })
                
        return signals
    
    def _is_breakout(self, segment: Dict, zhongshu: Dict) -> bool:
        """判断是否突破"""
        return (segment['end_price'] > zhongshu['high'] or 
                segment['end_price'] < zhongshu['low'])
    
    def _is_pullback(self, segment: Dict, zhongshu: Dict) -> bool:
        """判断是否回调"""
        return (zhongshu['low'] <= segment['end_price'] <= zhongshu['high'])
    
    def _calculate_analysis_result(self) -> Dict:
        """计算分析结果"""
        result = {
            'pen_count': len(self.pen_data),
            'segment_count': len(self.segment_data),
            'zhongshu_count': len(self.zhongshu_data),
            'trend_analysis': self._get_trend_summary(),
            'signal_count': len(self._generate_signals()),
            'risk_level': self._calculate_risk_level(),
            'recommendation': self._get_recommendation()
        }
        
        return result
    
    def _get_trend_summary(self) -> str:
        """获取趋势摘要"""
        if not self.trend_data:
            return "无趋势数据"
            
        trend = self.trend_data[0]
        return f"趋势类型: {trend['type']}, 方向: {trend['direction']}, 强度: {trend['strength']:.2f}"
    
    def _calculate_risk_level(self) -> str:
        """计算风险等级"""
        if not self.zhongshu_data:
            return "中等"
            
        avg_strength = sum(zs['strength'] for zs in self.zhongshu_data) / len(self.zhongshu_data)
        
        if avg_strength > 0.8:
            return "高"
        elif avg_strength > 0.5:
            return "中等"
        else:
            return "低"
    
    def _get_recommendation(self) -> str:
        """获取投资建议"""
        if not self.trend_data:
            return "建议观望"
            
        trend = self.trend_data[0]
        signals = self._generate_signals()
        
        if trend['direction'] == 'up' and any(s['type'] == 'breakout' for s in signals):
            return "建议买入"
        elif trend['direction'] == 'down' and any(s['type'] == 'breakout' for s in signals):
            return "建议卖出"
        else:
            return "建议观望"
    
    def create_chan_chart(self, stock_data: pd.DataFrame, analysis_result: Dict, save_path: str = None) -> str:
        """
        创建缠论分析图表
        
        参数:
            stock_data: 股票数据
            analysis_result: 分析结果
            save_path: 保存路径
            
        返回:
            str: 图表文件路径
        """
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[3, 1])
        
        # 主图：K线和缠论分析
        self._plot_main_chart(ax1, stock_data, analysis_result)
        
        # 副图：成交量
        self._plot_volume_chart(ax2, stock_data)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def _plot_main_chart(self, ax, stock_data: pd.DataFrame, analysis_result: Dict):
        """绘制主图"""
        # 绘制K线
        dates = pd.to_datetime(stock_data['date'])
        
        # 绘制笔
        pen_data = analysis_result.get('pen_data', [])
        for pen in pen_data:
            start_date = pd.to_datetime(pen['start_date'])
            end_date = pd.to_datetime(pen['end_date'])
            start_price = pen['start_price']
            end_price = pen['end_price']
            
            color = 'red' if pen['direction'] == 'up' else 'green'
            ax.plot([start_date, end_date], [start_price, end_price], 
                   color=color, linewidth=2, alpha=0.8)
            
            # 标记笔的端点
            ax.scatter([start_date, end_date], [start_price, end_price], 
                      color=color, s=50, zorder=5)
        
        # 绘制中枢
        zhongshu_data = analysis_result.get('zhongshu_data', [])
        for i, zs in enumerate(zhongshu_data):
            start_date = pd.to_datetime(zs['start_date'])
            end_date = pd.to_datetime(zs['end_date'])
            
            # 绘制中枢矩形
            rect = patches.Rectangle((start_date, zs['low']), 
                                   (end_date - start_date).days, 
                                   zs['high'] - zs['low'],
                                   linewidth=2, edgecolor='blue', 
                                   facecolor='lightblue', alpha=0.3)
            ax.add_patch(rect)
            
            # 标记中枢中心
            center_date = start_date + (end_date - start_date) / 2
            ax.text(center_date, zs['center'], f'中枢{i+1}', 
                   ha='center', va='center', fontsize=10, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        # 设置图表属性
        ax.set_title('缠论分析图', fontsize=16, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_volume_chart(self, ax, stock_data: pd.DataFrame):
        """绘制成交量图"""
        dates = pd.to_datetime(stock_data['date'])
        volumes = stock_data['volume']
        
        # 绘制成交量柱状图
        colors = ['red' if stock_data.iloc[i]['close'] >= stock_data.iloc[i]['open'] 
                 else 'green' for i in range(len(stock_data))]
        
        ax.bar(dates, volumes, color=colors, alpha=0.7)
        ax.set_title('成交量', fontsize=14)
        ax.set_ylabel('成交量', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
