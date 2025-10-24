#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缠论分析使用示例
演示如何使用缠论分析模块进行股票分析
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher import StockDataFetcher
from modules.chan_analyzer import ChanAnalyzer
from modules.chan_analysis_engine import ChanAnalysisEngine
from modules.chan_visualizer import ChanVisualizer

def main():
    """主函数：演示缠论分析功能"""
    print("=" * 60)
    print("缠论分析示例")
    print("=" * 60)
    
    # 股票代码
    stock_code = "000001"  # 平安银行
    period = "1年"
    
    print(f"正在分析股票: {stock_code}")
    print(f"分析周期: {period}")
    print()
    
    try:
        # 1. 获取股票数据
        print("1. 获取股票数据...")
        data_fetcher = StockDataFetcher()
        stock_data = data_fetcher.fetch_stock_data(stock_code, period)
        
        if stock_data.empty:
            print(f"❌ 无法获取股票 {stock_code} 的数据")
            return
        
        print(f"✅ 成功获取 {len(stock_data)} 条数据")
        print(f"   数据范围: {stock_data['date'].min()} 到 {stock_data['date'].max()}")
        print()
        
        # 2. 基础缠论分析
        print("2. 执行基础缠论分析...")
        chan_analyzer = ChanAnalyzer()
        basic_analysis = chan_analyzer.analyze(stock_data)
        
        print(f"✅ 识别出 {len(basic_analysis.get('pen_data', []))} 个笔")
        print(f"✅ 识别出 {len(basic_analysis.get('segment_data', []))} 个线段")
        print(f"✅ 识别出 {len(basic_analysis.get('zhongshu_data', []))} 个中枢")
        print()
        
        # 3. 高级缠论分析
        print("3. 执行高级缠论分析...")
        chan_analysis_engine = ChanAnalysisEngine()
        advanced_analysis = chan_analysis_engine.advanced_chan_analysis(stock_data)
        
        # 显示分析结果
        analysis_result = advanced_analysis.get('analysis_result', {})
        print(f"✅ 笔数量: {analysis_result.get('pen_count', 0)}")
        print(f"✅ 线段数量: {analysis_result.get('segment_count', 0)}")
        print(f"✅ 中枢数量: {analysis_result.get('zhongshu_count', 0)}")
        print(f"✅ 信号数量: {analysis_result.get('signal_count', 0)}")
        print(f"✅ 风险等级: {analysis_result.get('risk_level', '未知')}")
        print(f"✅ 投资建议: {analysis_result.get('recommendation', '观望')}")
        print()
        
        # 4. 生成分析报告
        print("4. 生成分析报告...")
        chan_visualizer = ChanVisualizer()
        analysis_report = chan_visualizer.create_chan_analysis_report(advanced_analysis, stock_code)
        
        # 保存报告
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        
        report_path = os.path.join(output_dir, f"{stock_code}_chan_analysis_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(analysis_report)
        
        print(f"✅ 分析报告已保存至: {report_path}")
        print()
        
        # 5. 生成可视化图表
        print("5. 生成可视化图表...")
        chart_path = chan_visualizer.create_comprehensive_chan_chart(
            stock_data, advanced_analysis,
            os.path.join(output_dir, f"charts/{stock_code}_chan_analysis.png")
        )
        
        print(f"✅ 缠论分析图表已保存至: {chart_path}")
        print()
        
        # 6. 显示详细分析结果
        print("6. 详细分析结果:")
        print("-" * 40)
        
        # 显示笔分析
        pen_data = basic_analysis.get('pen_data', [])
        if pen_data:
            print("📊 笔分析:")
            for i, pen in enumerate(pen_data[-3:]):  # 显示最近3个笔
                print(f"   笔{i+1}: {pen['start_date']} → {pen['end_date']}")
                print(f"         方向: {pen['direction']}, 长度: {pen['length']}天")
                print(f"         价格: {pen['start_price']:.2f} → {pen['end_price']:.2f}")
            print()
        
        # 显示线段分析
        segment_data = basic_analysis.get('segment_data', [])
        if segment_data:
            print("📈 线段分析:")
            for i, segment in enumerate(segment_data[-2:]):  # 显示最近2个线段
                print(f"   线段{i+1}: {segment['start_date']} → {segment['end_date']}")
                print(f"          方向: {segment['direction']}, 长度: {segment['length']}笔")
                print(f"          价格: {segment['start_price']:.2f} → {segment['end_price']:.2f}")
            print()
        
        # 显示中枢分析
        zhongshu_data = basic_analysis.get('zhongshu_data', [])
        if zhongshu_data:
            print("🎯 中枢分析:")
            for i, zs in enumerate(zhongshu_data):
                print(f"   中枢{i+1}: {zs['start_date']} → {zs['end_date']}")
                print(f"          价格区间: {zs['low']:.2f} - {zs['high']:.2f}")
                print(f"          中心价格: {zs['center']:.2f}")
                print(f"          强度: {zs['strength']:.2f}")
            print()
        
        # 显示交易信号
        signals = basic_analysis.get('signals', [])
        if signals:
            print("🚦 交易信号:")
            for i, signal in enumerate(signals):
                print(f"   信号{i+1}: {signal['type']}")
                print(f"          方向: {signal['direction']}")
                print(f"          强度: {signal['strength']}")
                print(f"          置信度: {signal['confidence']:.2f}")
            print()
        
        # 显示投资建议
        investment_advice = advanced_analysis.get('investment_advice', {})
        if investment_advice:
            print("💡 投资建议:")
            print(f"   操作建议: {investment_advice.get('action', '观望')}")
            print(f"   置信度: {investment_advice.get('confidence', 0):.2f}")
            print(f"   时间周期: {investment_advice.get('time_horizon', '短期')}")
            print(f"   风险等级: {investment_advice.get('risk_level', '中等')}")
            
            reasoning = investment_advice.get('reasoning', [])
            if reasoning:
                print("   分析理由:")
                for reason in reasoning:
                    print(f"     • {reason}")
            print()
        
        print("=" * 60)
        print("缠论分析完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
