import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ChanAnalysisEngine:
    """
    缠论分析引擎，提供高级分析功能和交易信号生成
    """
    
    def __init__(self):
        self.analysis_config = {
            'min_pen_length': 3,  # 最小笔长度
            'min_segment_length': 2,  # 最小线段长度
            'zhongshu_min_segments': 3,  # 中枢最小线段数
            'trend_threshold': 0.6,  # 趋势判断阈值
            'signal_confidence_threshold': 0.5  # 信号置信度阈值
        }
    
    def advanced_chan_analysis(self, stock_data: pd.DataFrame) -> Dict:
        """
        执行高级缠论分析
        
        参数:
            stock_data: 股票数据
            
        返回:
            dict: 完整的缠论分析结果
        """
        if stock_data.empty:
            return {}
        
        # 确保数据按时间排序
        stock_data = stock_data.sort_values('date').reset_index(drop=True)
        
        # 1. 基础缠论分析
        from .chan_analyzer import ChanAnalyzer
        chan_analyzer = ChanAnalyzer()
        basic_analysis = chan_analyzer.analyze(stock_data)
        
        # 2. 高级分析
        advanced_features = self._perform_advanced_analysis(stock_data, basic_analysis)
        
        # 3. 趋势分析
        trend_analysis = self._analyze_trend_structure(basic_analysis)
        
        # 4. 买卖点分析
        trading_points = self._identify_trading_points(basic_analysis)
        
        # 5. 风险评估
        risk_assessment = self._assess_risk(basic_analysis, stock_data)
        
        # 6. 综合评分
        overall_score = self._calculate_overall_score(basic_analysis, advanced_features, risk_assessment)
        
        # 7. 生成投资建议
        investment_advice = self._generate_investment_advice(
            basic_analysis, advanced_features, trend_analysis, 
            trading_points, risk_assessment, overall_score
        )
        
        return {
            'basic_analysis': basic_analysis,
            'advanced_features': advanced_features,
            'trend_analysis': trend_analysis,
            'trading_points': trading_points,
            'risk_assessment': risk_assessment,
            'overall_score': overall_score,
            'investment_advice': investment_advice,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _perform_advanced_analysis(self, stock_data: pd.DataFrame, basic_analysis: Dict) -> Dict:
        """执行高级分析"""
        advanced_features = {}
        
        # 1. 笔的质量分析
        pen_quality = self._analyze_pen_quality(basic_analysis.get('pen_data', []))
        advanced_features['pen_quality'] = pen_quality
        
        # 2. 线段强度分析
        segment_strength = self._analyze_segment_strength(basic_analysis.get('segment_data', []))
        advanced_features['segment_strength'] = segment_strength
        
        # 3. 中枢稳定性分析
        zhongshu_stability = self._analyze_zhongshu_stability(basic_analysis.get('zhongshu_data', []))
        advanced_features['zhongshu_stability'] = zhongshu_stability
        
        # 4. 价格动量分析
        price_momentum = self._analyze_price_momentum(stock_data)
        advanced_features['price_momentum'] = price_momentum
        
        # 5. 成交量配合分析
        volume_analysis = self._analyze_volume_pattern(stock_data)
        advanced_features['volume_analysis'] = volume_analysis
        
        return advanced_features
    
    def _analyze_pen_quality(self, pen_data: List[Dict]) -> Dict:
        """分析笔的质量"""
        if not pen_data:
            return {'quality_score': 0, 'analysis': '无笔数据'}
        
        quality_scores = []
        analysis_points = []
        
        for pen in pen_data:
            # 计算笔的长度质量
            length_score = min(1.0, pen['length'] / 10)  # 长度越长质量越高
            
            # 计算价格变化幅度
            price_change = abs(pen['end_price'] - pen['start_price'])
            price_score = min(1.0, price_change / (pen['start_price'] * 0.1))  # 10%以上变化为满分
            
            # 综合评分
            pen_score = (length_score + price_score) / 2
            quality_scores.append(pen_score)
            
            if pen_score > 0.8:
                analysis_points.append(f"高质量笔: 长度{pen['length']}天, 变化{price_change:.2f}")
            elif pen_score > 0.5:
                analysis_points.append(f"中等质量笔: 长度{pen['length']}天, 变化{price_change:.2f}")
            else:
                analysis_points.append(f"低质量笔: 长度{pen['length']}天, 变化{price_change:.2f}")
        
        overall_quality = np.mean(quality_scores) if quality_scores else 0
        
        return {
            'quality_score': overall_quality,
            'pen_scores': quality_scores,
            'analysis': analysis_points,
            'high_quality_count': sum(1 for score in quality_scores if score > 0.8),
            'total_pens': len(pen_data)
        }
    
    def _analyze_segment_strength(self, segment_data: List[Dict]) -> Dict:
        """分析线段强度"""
        if not segment_data:
            return {'strength_score': 0, 'analysis': '无线段数据'}
        
        strength_scores = []
        analysis_points = []
        
        for segment in segment_data:
            # 计算线段长度
            length_score = min(1.0, segment['length'] / 5)  # 5个笔以上为满分
            
            # 计算价格变化幅度
            price_change = abs(segment['end_price'] - segment['start_price'])
            price_score = min(1.0, price_change / (segment['start_price'] * 0.2))  # 20%以上变化为满分
            
            # 计算方向一致性
            direction_consistency = 1.0 if segment['direction'] in ['up', 'down'] else 0.5
            
            # 综合评分
            segment_score = (length_score + price_score + direction_consistency) / 3
            strength_scores.append(segment_score)
            
            if segment_score > 0.8:
                analysis_points.append(f"强线段: 方向{segment['direction']}, 长度{segment['length']}笔")
            elif segment_score > 0.5:
                analysis_points.append(f"中等线段: 方向{segment['direction']}, 长度{segment['length']}笔")
            else:
                analysis_points.append(f"弱线段: 方向{segment['direction']}, 长度{segment['length']}笔")
        
        overall_strength = np.mean(strength_scores) if strength_scores else 0
        
        return {
            'strength_score': overall_strength,
            'segment_scores': strength_scores,
            'analysis': analysis_points,
            'strong_segments': sum(1 for score in strength_scores if score > 0.8),
            'total_segments': len(segment_data)
        }
    
    def _analyze_zhongshu_stability(self, zhongshu_data: List[Dict]) -> Dict:
        """分析中枢稳定性"""
        if not zhongshu_data:
            return {'stability_score': 0, 'analysis': '无中枢数据'}
        
        stability_scores = []
        analysis_points = []
        
        for zs in zhongshu_data:
            # 计算中枢强度
            strength_score = zs.get('strength', 0)
            
            # 计算价格区间稳定性
            range_stability = min(1.0, 1 - (zs['range'] / zs['center']))  # 区间越小越稳定
            
            # 计算时间跨度
            time_span = (pd.to_datetime(zs['end_date']) - pd.to_datetime(zs['start_date'])).days
            time_score = min(1.0, time_span / 30)  # 30天以上为满分
            
            # 综合评分
            stability_score = (strength_score + range_stability + time_score) / 3
            stability_scores.append(stability_score)
            
            if stability_score > 0.8:
                analysis_points.append(f"稳定中枢: 强度{strength_score:.2f}, 区间{zs['range']:.2f}")
            elif stability_score > 0.5:
                analysis_points.append(f"中等中枢: 强度{strength_score:.2f}, 区间{zs['range']:.2f}")
            else:
                analysis_points.append(f"不稳定中枢: 强度{strength_score:.2f}, 区间{zs['range']:.2f}")
        
        overall_stability = np.mean(stability_scores) if stability_scores else 0
        
        return {
            'stability_score': overall_stability,
            'zhongshu_scores': stability_scores,
            'analysis': analysis_points,
            'stable_zhongshu': sum(1 for score in stability_scores if score > 0.8),
            'total_zhongshu': len(zhongshu_data)
        }
    
    def _analyze_price_momentum(self, stock_data: pd.DataFrame) -> Dict:
        """分析价格动量"""
        if len(stock_data) < 20:
            return {'momentum_score': 0, 'analysis': '数据不足'}
        
        # 计算短期和长期动量
        short_momentum = (stock_data['close'].iloc[-1] - stock_data['close'].iloc[-5]) / stock_data['close'].iloc[-5]
        long_momentum = (stock_data['close'].iloc[-1] - stock_data['close'].iloc[-20]) / stock_data['close'].iloc[-20]
        
        # 计算动量一致性
        momentum_consistency = 1.0 if (short_momentum > 0 and long_momentum > 0) or (short_momentum < 0 and long_momentum < 0) else 0.5
        
        # 计算动量强度
        momentum_strength = (abs(short_momentum) + abs(long_momentum)) / 2
        
        # 综合评分
        momentum_score = (momentum_consistency + min(1.0, momentum_strength * 10)) / 2
        
        analysis = []
        if momentum_score > 0.8:
            analysis.append("强动量: 短期和长期动量一致且强劲")
        elif momentum_score > 0.5:
            analysis.append("中等动量: 动量方向一致但强度一般")
        else:
            analysis.append("弱动量: 动量方向不一致或强度不足")
        
        return {
            'momentum_score': momentum_score,
            'short_momentum': short_momentum,
            'long_momentum': long_momentum,
            'momentum_consistency': momentum_consistency,
            'analysis': analysis
        }
    
    def _analyze_volume_pattern(self, stock_data: pd.DataFrame) -> Dict:
        """分析成交量模式"""
        if len(stock_data) < 10:
            return {'volume_score': 0, 'analysis': '数据不足'}
        
        # 计算成交量移动平均
        volume_ma5 = stock_data['volume'].rolling(window=5).mean()
        volume_ma10 = stock_data['volume'].rolling(window=10).mean()
        
        # 计算成交量趋势
        recent_volume = stock_data['volume'].iloc[-5:].mean()
        avg_volume = stock_data['volume'].mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # 计算成交量与价格的相关性
        price_change = stock_data['close'].pct_change()
        volume_change = stock_data['volume'].pct_change()
        correlation = price_change.corr(volume_change) if len(price_change) > 1 else 0
        
        # 综合评分
        volume_score = (min(1.0, volume_ratio) + max(0, correlation)) / 2
        
        analysis = []
        if volume_score > 0.8:
            analysis.append("成交量配合良好: 量价关系健康")
        elif volume_score > 0.5:
            analysis.append("成交量配合一般: 量价关系正常")
        else:
            analysis.append("成交量配合不佳: 量价关系异常")
        
        return {
            'volume_score': volume_score,
            'volume_ratio': volume_ratio,
            'correlation': correlation,
            'recent_volume': recent_volume,
            'avg_volume': avg_volume,
            'analysis': analysis
        }
    
    def _analyze_trend_structure(self, basic_analysis: Dict) -> Dict:
        """分析趋势结构"""
        segment_data = basic_analysis.get('segment_data', [])
        zhongshu_data = basic_analysis.get('zhongshu_data', [])
        
        if not segment_data:
            return {'trend_structure': 'unknown', 'confidence': 0}
        
        # 分析最近线段的趋势
        recent_segments = segment_data[-3:] if len(segment_data) >= 3 else segment_data
        
        # 计算趋势方向
        up_segments = sum(1 for seg in recent_segments if seg['direction'] == 'up')
        down_segments = sum(1 for seg in recent_segments if seg['direction'] == 'down')
        
        if up_segments > down_segments:
            trend_direction = 'up'
            trend_strength = up_segments / len(recent_segments)
        elif down_segments > up_segments:
            trend_direction = 'down'
            trend_strength = down_segments / len(recent_segments)
        else:
            trend_direction = 'sideways'
            trend_strength = 0.5
        
        # 分析中枢对趋势的影响
        zhongshu_impact = 0
        if zhongshu_data:
            latest_zhongshu = zhongshu_data[-1]
            latest_segment = recent_segments[-1] if recent_segments else None
            
            if latest_segment:
                # 判断是否突破中枢
                if (latest_segment['end_price'] > latest_zhongshu['high'] or 
                    latest_segment['end_price'] < latest_zhongshu['low']):
                    zhongshu_impact = 0.8  # 突破中枢，趋势加强
                else:
                    zhongshu_impact = 0.3  # 在中枢内震荡
        
        # 综合趋势分析
        overall_confidence = (trend_strength + zhongshu_impact) / 2
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'zhongshu_impact': zhongshu_impact,
            'confidence': overall_confidence,
            'recent_segments_count': len(recent_segments),
            'up_segments': up_segments,
            'down_segments': down_segments
        }
    
    def _identify_trading_points(self, basic_analysis: Dict) -> Dict:
        """识别交易点"""
        signals = basic_analysis.get('signals', [])
        segment_data = basic_analysis.get('segment_data', [])
        zhongshu_data = basic_analysis.get('zhongshu_data', [])
        
        trading_points = {
            'buy_signals': [],
            'sell_signals': [],
            'hold_signals': [],
            'total_signals': len(signals)
        }
        
        # 分析现有信号
        for signal in signals:
            if signal['type'] == 'breakout':
                if signal['direction'] == 'up':
                    trading_points['buy_signals'].append({
                        'type': 'breakout_buy',
                        'confidence': signal['confidence'],
                        'strength': signal['strength'],
                        'description': '向上突破信号'
                    })
                else:
                    trading_points['sell_signals'].append({
                        'type': 'breakout_sell',
                        'confidence': signal['confidence'],
                        'strength': signal['strength'],
                        'description': '向下突破信号'
                    })
            elif signal['type'] == 'pullback':
                trading_points['hold_signals'].append({
                    'type': 'pullback_hold',
                    'confidence': signal['confidence'],
                    'strength': signal['strength'],
                    'description': '回调信号，建议观望'
                })
        
        # 基于中枢分析交易点
        if zhongshu_data and segment_data:
            latest_zhongshu = zhongshu_data[-1]
            latest_segment = segment_data[-1]
            
            # 判断是否接近中枢边界
            price = latest_segment['end_price']
            zhongshu_high = latest_zhongshu['high']
            zhongshu_low = latest_zhongshu['low']
            zhongshu_center = latest_zhongshu['center']
            
            if price > zhongshu_high:
                trading_points['buy_signals'].append({
                    'type': 'zhongshu_breakout_buy',
                    'confidence': 0.7,
                    'strength': 'strong',
                    'description': '突破中枢上沿，买入信号'
                })
            elif price < zhongshu_low:
                trading_points['sell_signals'].append({
                    'type': 'zhongshu_breakout_sell',
                    'confidence': 0.7,
                    'strength': 'strong',
                    'description': '跌破中枢下沿，卖出信号'
                })
            elif zhongshu_low <= price <= zhongshu_center:
                trading_points['buy_signals'].append({
                    'type': 'zhongshu_support_buy',
                    'confidence': 0.5,
                    'strength': 'medium',
                    'description': '接近中枢下沿，支撑买入'
                })
            elif zhongshu_center <= price <= zhongshu_high:
                trading_points['sell_signals'].append({
                    'type': 'zhongshu_resistance_sell',
                    'confidence': 0.5,
                    'strength': 'medium',
                    'description': '接近中枢上沿，阻力卖出'
                })
        
        return trading_points
    
    def _assess_risk(self, basic_analysis: Dict, stock_data: pd.DataFrame) -> Dict:
        """评估风险"""
        risk_factors = []
        risk_score = 0
        
        # 1. 数据质量风险
        pen_count = len(basic_analysis.get('pen_data', []))
        segment_count = len(basic_analysis.get('segment_data', []))
        
        if pen_count < 5:
            risk_factors.append("笔数量不足，分析可靠性低")
            risk_score += 0.3
        
        if segment_count < 2:
            risk_factors.append("线段数量不足，趋势判断困难")
            risk_score += 0.2
        
        # 2. 价格波动风险
        if len(stock_data) >= 20:
            recent_volatility = stock_data['close'].pct_change().std()
            if recent_volatility > 0.05:  # 5%以上波动
                risk_factors.append("价格波动较大，风险较高")
                risk_score += 0.3
            elif recent_volatility > 0.03:  # 3%以上波动
                risk_factors.append("价格波动适中")
                risk_score += 0.1
        
        # 3. 中枢稳定性风险
        zhongshu_data = basic_analysis.get('zhongshu_data', [])
        if zhongshu_data:
            avg_strength = np.mean([zs.get('strength', 0) for zs in zhongshu_data])
            if avg_strength < 0.3:
                risk_factors.append("中枢稳定性差，趋势不明确")
                risk_score += 0.2
        
        # 4. 成交量风险
        if len(stock_data) >= 10:
            recent_volume = stock_data['volume'].iloc[-5:].mean()
            avg_volume = stock_data['volume'].mean()
            if recent_volume < avg_volume * 0.5:
                risk_factors.append("成交量萎缩，流动性风险")
                risk_score += 0.2
        
        # 综合风险等级
        if risk_score >= 0.7:
            risk_level = 'high'
        elif risk_score >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'pen_count': pen_count,
            'segment_count': segment_count,
            'recent_volatility': stock_data['close'].pct_change().std() if len(stock_data) > 1 else 0
        }
    
    def _calculate_overall_score(self, basic_analysis: Dict, advanced_features: Dict, 
                               risk_assessment: Dict) -> Dict:
        """计算综合评分"""
        scores = []
        
        # 1. 基础分析评分
        pen_quality = advanced_features.get('pen_quality', {}).get('quality_score', 0)
        segment_strength = advanced_features.get('segment_strength', {}).get('strength_score', 0)
        zhongshu_stability = advanced_features.get('zhongshu_stability', {}).get('stability_score', 0)
        
        basic_score = (pen_quality + segment_strength + zhongshu_stability) / 3
        scores.append(('基础分析', basic_score, 0.3))
        
        # 2. 技术指标评分
        momentum_score = advanced_features.get('price_momentum', {}).get('momentum_score', 0)
        volume_score = advanced_features.get('volume_analysis', {}).get('volume_score', 0)
        
        technical_score = (momentum_score + volume_score) / 2
        scores.append(('技术指标', technical_score, 0.25))
        
        # 3. 趋势分析评分
        trend_analysis = basic_analysis.get('trend_data', [])
        if trend_analysis:
            trend_score = trend_analysis[0].get('strength', 0)
        else:
            trend_score = 0
        scores.append(('趋势分析', trend_score, 0.25))
        
        # 4. 风险调整评分
        risk_score = risk_assessment.get('risk_score', 0)
        risk_adjusted_score = max(0, 1 - risk_score)
        scores.append(('风险调整', risk_adjusted_score, 0.2))
        
        # 计算加权总分
        weighted_score = sum(score * weight for _, score, weight in scores)
        
        # 评级
        if weighted_score >= 0.8:
            grade = 'A'
            grade_desc = '优秀'
        elif weighted_score >= 0.7:
            grade = 'B'
            grade_desc = '良好'
        elif weighted_score >= 0.6:
            grade = 'C'
            grade_desc = '一般'
        elif weighted_score >= 0.5:
            grade = 'D'
            grade_desc = '较差'
        else:
            grade = 'F'
            grade_desc = '很差'
        
        return {
            'overall_score': weighted_score,
            'grade': grade,
            'grade_description': grade_desc,
            'component_scores': scores,
            'risk_adjusted_score': risk_adjusted_score,
            'recommendation_strength': min(1.0, weighted_score * 1.2)
        }
    
    def _generate_investment_advice(self, basic_analysis: Dict, advanced_features: Dict,
                                  trend_analysis: Dict, trading_points: Dict,
                                  risk_assessment: Dict, overall_score: Dict) -> Dict:
        """生成投资建议"""
        advice = {
            'action': 'hold',
            'confidence': 0.5,
            'reasoning': [],
            'target_price': None,
            'stop_loss': None,
            'time_horizon': 'short',
            'risk_level': risk_assessment.get('risk_level', 'medium')
        }
        
        # 基于综合评分决定主要行动
        overall_score_value = overall_score.get('overall_score', 0)
        grade = overall_score.get('grade', 'F')
        
        # 买入条件
        buy_signals = trading_points.get('buy_signals', [])
        sell_signals = trading_points.get('sell_signals', [])
        
        if (overall_score_value >= 0.7 and 
            len(buy_signals) > len(sell_signals) and
            risk_assessment.get('risk_level') != 'high'):
            advice['action'] = 'buy'
            advice['confidence'] = min(0.9, overall_score_value + 0.1)
            advice['reasoning'].append(f"综合评分{grade}级，买入信号占优")
            
            # 设置目标价格和止损
            if basic_analysis.get('segment_data'):
                latest_segment = basic_analysis['segment_data'][-1]
                if latest_segment['direction'] == 'up':
                    advice['target_price'] = latest_segment['end_price'] * 1.1  # 10%目标
                    advice['stop_loss'] = latest_segment['end_price'] * 0.95   # 5%止损
        
        # 卖出条件
        elif (overall_score_value < 0.4 or 
              len(sell_signals) > len(buy_signals) or
              risk_assessment.get('risk_level') == 'high'):
            advice['action'] = 'sell'
            advice['confidence'] = min(0.9, 1 - overall_score_value + 0.1)
            advice['reasoning'].append(f"综合评分{grade}级，卖出信号占优或风险较高")
        
        # 观望条件
        else:
            advice['action'] = 'hold'
            advice['confidence'] = 0.6
            advice['reasoning'].append("信号不明确，建议观望")
        
        # 添加具体分析理由
        if advanced_features.get('pen_quality', {}).get('quality_score', 0) > 0.7:
            advice['reasoning'].append("笔的质量较高")
        
        if advanced_features.get('segment_strength', {}).get('strength_score', 0) > 0.7:
            advice['reasoning'].append("线段强度良好")
        
        if advanced_features.get('zhongshu_stability', {}).get('stability_score', 0) > 0.7:
            advice['reasoning'].append("中枢稳定性好")
        
        # 风险提示
        risk_factors = risk_assessment.get('risk_factors', [])
        if risk_factors:
            advice['reasoning'].extend([f"风险提示: {factor}" for factor in risk_factors[:2]])
        
        # 时间周期建议
        if trend_analysis.get('trend_direction') == 'up':
            advice['time_horizon'] = 'medium'
        elif trend_analysis.get('trend_direction') == 'down':
            advice['time_horizon'] = 'short'
        else:
            advice['time_horizon'] = 'short'
        
        return advice
