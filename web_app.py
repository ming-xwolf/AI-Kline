import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.visualizer import Visualizer
from modules.ai_analyzer import AIAnalyzer
from modules.chan_analyzer import ChanAnalyzer
from modules.chan_analysis_engine import ChanAnalysisEngine
from modules.chan_visualizer import ChanVisualizer
from dotenv import load_dotenv
import matplotlib
# 设置 matplotlib 使用非 GUI 后端以避免 tkinter 依赖
matplotlib.use('Agg')

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# 确保输出目录存在
os.makedirs('./output', exist_ok=True)
os.makedirs('./output/charts', exist_ok=True)

# 初始化各模块
data_fetcher = StockDataFetcher()
technical_analyzer = TechnicalAnalyzer()
visualizer = Visualizer()
ai_analyzer = AIAnalyzer()
chan_analyzer = ChanAnalyzer()
chan_analysis_engine = ChanAnalysisEngine()
chan_visualizer = ChanVisualizer()

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析股票"""
    data = request.form
    stock_code = data.get('stock_code')
    period = data.get('period', '1年')
    save_path = './output'
    
    if not stock_code:
        return jsonify({'error': '请输入股票代码'}), 400
    
    try:
        # 获取股票数据
        stock_data = data_fetcher.fetch_stock_data(stock_code, period)
        
        if stock_data.empty:
            return jsonify({'error': f'未找到股票 {stock_code} 的数据'}), 404
        
        # 获取财务和新闻数据
        financial_data = data_fetcher.fetch_financial_data(stock_code)
        news_data = data_fetcher.fetch_news_data(stock_code)
        
        # 计算技术指标
        indicators = technical_analyzer.calculate_indicators(stock_data)
        
        # 生成可视化图表
        chart_path = visualizer.create_charts(stock_data, indicators, stock_code, save_path)
        
        # AI分析预测
        analysis_result = ai_analyzer.analyze(stock_data, indicators, financial_data, news_data, stock_code, save_path)
        
        # 保存分析结果
        result_path = os.path.join(save_path, f"{stock_code}_analysis_result.txt")
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(analysis_result)
        
        # 准备返回数据
        chart_files = []
        for file in os.listdir(os.path.join(save_path, 'charts')):
            if file.startswith(stock_code) and (file.endswith('.png') or file.endswith('.html')):
                chart_files.append(file)
        
        return jsonify({
            'success': True,
            'stock_code': stock_code,
            'charts': chart_files,
            'analysis_result': analysis_result
        })
    
    except Exception as e:
        return jsonify({'error': f'分析过程中出错: {str(e)}'}), 500

@app.route('/output/charts/<path:filename>')
def serve_chart(filename):
    """提供图表文件"""
    return send_from_directory('output/charts', filename)

@app.route('/stock_info/<stock_code>')
def get_stock_info(stock_code):
    """获取股票基本信息"""
    try:
        import akshare as ak
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        if not stock_info.empty:
            # 转换为字典列表
            info_dict = {
                row['item']: row['value'] 
                for _, row in stock_info.iterrows()
            }
            return jsonify({'success': True, 'data': info_dict})
        else:
            return jsonify({'error': f'未找到股票 {stock_code} 的信息'}), 404
    except Exception as e:
        return jsonify({'error': f'获取股票信息时出错: {str(e)}'}), 500

@app.route('/chan_analyze', methods=['POST'])
def chan_analyze():
    """缠论分析"""
    data = request.form
    stock_code = data.get('stock_code')
    period = data.get('period', '1年')
    
    if not stock_code:
        return jsonify({'error': '请输入股票代码'}), 400
    
    try:
        # 获取股票数据
        stock_data = data_fetcher.fetch_stock_data(stock_code, period)
        
        if stock_data.empty:
            return jsonify({'error': f'未找到股票 {stock_code} 的数据'}), 404
        
        # 执行缠论分析
        chan_analysis = chan_analysis_engine.advanced_chan_analysis(stock_data)
        
        # 生成缠论分析图表
        chart_path = chan_visualizer.create_comprehensive_chan_chart(
            stock_data, chan_analysis, 
            f'./output/charts/{stock_code}_chan_analysis.png'
        )
        
        # 生成分析报告
        chan_report = chan_visualizer.create_chan_analysis_report(chan_analysis, stock_code)
        
        return jsonify({
            'success': True,
            'chart_path': chart_path,
            'analysis_report': chan_report,
            'analysis_data': {
                'pen_count': chan_analysis.get('basic_analysis', {}).get('pen_data', []).__len__(),
                'segment_count': chan_analysis.get('basic_analysis', {}).get('segment_data', []).__len__(),
                'zhongshu_count': chan_analysis.get('basic_analysis', {}).get('zhongshu_data', []).__len__(),
                'overall_score': chan_analysis.get('overall_score', {}).get('overall_score', 0),
                'investment_advice': chan_analysis.get('investment_advice', {})
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'缠论分析时出错: {str(e)}'}), 500

@app.route('/chan_chart', methods=['POST'])
def chan_chart():
    """生成缠论分析图表"""
    data = request.form
    stock_code = data.get('stock_code')
    period = data.get('period', '1年')
    
    if not stock_code:
        return jsonify({'error': '请输入股票代码'}), 400
    
    try:
        # 获取股票数据
        stock_data = data_fetcher.fetch_stock_data(stock_code, period)
        
        if stock_data.empty:
            return jsonify({'error': f'未找到股票 {stock_code} 的数据'}), 404
        
        # 执行缠论分析
        chan_analysis = chan_analysis_engine.advanced_chan_analysis(stock_data)
        
        # 生成缠论分析图表
        chart_path = chan_visualizer.create_comprehensive_chan_chart(
            stock_data, chan_analysis, 
            f'./output/charts/{stock_code}_chan_analysis.png'
        )
        
        return jsonify({
            'success': True,
            'chart_path': chart_path
        })
        
    except Exception as e:
        return jsonify({'error': f'生成缠论图表时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000, threaded=False)  # 禁用多线程